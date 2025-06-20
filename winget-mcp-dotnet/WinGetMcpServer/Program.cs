using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using WinGetMcpServer.Infrastructure;
using WinGetMcpServer.Configuration;
using WinGetMcpServer.Tools;
using WinGetMcpServer.Services;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace WinGetMcpServer;

class Program
{
    private static IServiceProvider? _serviceProvider;
    private static ILogger<Program>? _logger;

    static async Task<int> Main(string[] args)
    {
        try
        {
            var host = CreateHostBuilder(args).Build();
            _serviceProvider = host.Services;
            _logger = _serviceProvider.GetRequiredService<ILogger<Program>>();

            // Validate service registration
            host.Services.ValidateServices();
            
            _logger.LogInformation("WinGet MCP Server starting...");

            // Test the WinGet service availability
            var winGetService = host.Services.GetRequiredService<IWinGetService>();
            var isAvailable = await winGetService.IsAvailableAsync();
            
            if (!isAvailable)
            {
                _logger.LogWarning("WinGet APIs are not available - server will run in limited mode");
            }
            else
            {
                _logger.LogInformation("WinGet APIs are available and ready");
            }

            _logger.LogInformation("WinGet MCP Server started successfully");

            // Run MCP protocol loop
            await RunMcpServerAsync();
            
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Fatal error starting WinGet MCP Server: {ex.Message}");
            return 1;
        }
    }

    static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureAppConfiguration((context, config) =>
            {
                config.AddJsonFile("appsettings.json", optional: true);
                config.AddEnvironmentVariables();
                config.AddCommandLine(args);
            })
            .ConfigureServices((context, services) =>
            {
                // Add WinGet MCP Server services
                services.AddWinGetMcpServer(context.Configuration);
                services.AddMcpProtocol();
            });

    static async Task RunMcpServerAsync()
    {
        using var reader = new StreamReader(Console.OpenStandardInput());
        using var writer = new StreamWriter(Console.OpenStandardOutput()) { AutoFlush = true };

        string? line;
        while ((line = await reader.ReadLineAsync()) != null)
        {
            try
            {
                var request = JsonSerializer.Deserialize<JsonObject>(line);
                if (request == null) continue;

                var response = await HandleMcpRequestAsync(request);
                if (response != null)
                {
                    var responseJson = JsonSerializer.Serialize(response);
                    await writer.WriteLineAsync(responseJson);
                }
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error processing MCP request: {Request}", line);
                
                // Send error response
                var errorResponse = new JsonObject
                {
                    ["jsonrpc"] = "2.0",
                    ["error"] = new JsonObject
                    {
                        ["code"] = -32603,
                        ["message"] = "Internal error",
                        ["data"] = ex.Message
                    }
                };

                var errorJson = JsonSerializer.Serialize(errorResponse);
                await writer.WriteLineAsync(errorJson);
            }
        }
    }

    static async Task<JsonObject?> HandleMcpRequestAsync(JsonObject request)
    {
        var method = request["method"]?.GetValue<string>();
        var id = request["id"];
        var parameters = request["params"] as JsonObject;

        _logger?.LogDebug("Handling MCP request: {Method}", method);

        // Handle notifications (requests without ID)
        if (id == null)
        {
            return null; // Don't send response for notifications
        }

        return method switch
        {
            "initialize" => HandleInitialize(id),
            "tools/list" => HandleToolsList(id),
            "tools/call" => await HandleToolsCallAsync(id, parameters),
            _ => new JsonObject
            {
                ["jsonrpc"] = "2.0",
                ["id"] = id?.DeepClone(),
                ["error"] = new JsonObject
                {
                    ["code"] = -32601,
                    ["message"] = "Method not found"
                }
            }
        };
    }

    static JsonObject HandleInitialize(JsonNode? id)
    {
        return new JsonObject
        {
            ["jsonrpc"] = "2.0",
            ["id"] = id?.DeepClone(),
            ["result"] = new JsonObject
            {
                ["protocolVersion"] = "2024-11-05",
                ["capabilities"] = new JsonObject
                {
                    ["tools"] = new JsonObject()
                },
                ["serverInfo"] = new JsonObject
                {
                    ["name"] = "winget-mcp-server",
                    ["version"] = "1.0.0"
                }
            }
        };
    }

    static JsonObject HandleToolsList(JsonNode? id)
    {
        var tools = new JsonArray
        {
            new JsonObject
            {
                ["name"] = "search",
                ["description"] = "Search for packages using WinGet",
                ["inputSchema"] = new JsonObject
                {
                    ["type"] = "object",
                    ["properties"] = new JsonObject
                    {
                        ["query"] = new JsonObject
                        {
                            ["type"] = "string",
                            ["description"] = "Search query for packages"
                        },
                        ["limit"] = new JsonObject
                        {
                            ["type"] = "integer",
                            ["description"] = "Maximum number of results to return",
                            ["default"] = 10
                        }
                    },
                    ["required"] = new JsonArray { "query" }
                }
            }
        };

        return new JsonObject
        {
            ["jsonrpc"] = "2.0",
            ["id"] = id?.DeepClone(),
            ["result"] = new JsonObject
            {
                ["tools"] = tools
            }
        };
    }

    static async Task<JsonObject> HandleToolsCallAsync(JsonNode? id, JsonObject? parameters)
    {
        try
        {
            var name = parameters?["name"]?.GetValue<string>();
            var arguments = parameters?["arguments"] as JsonObject;

            if (name == "search" && _serviceProvider != null)
            {
                var searchTool = _serviceProvider.GetRequiredService<SearchTool>();
                var query = arguments?["query"]?.GetValue<string>() ?? "";
                var limit = arguments?["limit"]?.GetValue<int>() ?? 10;

                var request = new SearchRequest { Query = query, Limit = limit };
                var result = await searchTool.ExecuteAsync(request);

                return new JsonObject
                {
                    ["jsonrpc"] = "2.0",
                    ["id"] = id?.DeepClone(),
                    ["result"] = new JsonObject
                    {
                        ["content"] = new JsonArray
                        {
                            new JsonObject
                            {
                                ["type"] = "text",
                                ["text"] = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true })
                            }
                        }
                    }
                };
            }

            return new JsonObject
            {
                ["jsonrpc"] = "2.0",
                ["id"] = id?.DeepClone(),
                ["error"] = new JsonObject
                {
                    ["code"] = -32602,
                    ["message"] = "Invalid params"
                }
            };
        }
        catch (Exception ex)
        {
            _logger?.LogError(ex, "Error executing tool call");
            
            return new JsonObject
            {
                ["jsonrpc"] = "2.0",
                ["id"] = id?.DeepClone(),
                ["error"] = new JsonObject
                {
                    ["code"] = -32603,
                    ["message"] = "Internal error",
                    ["data"] = ex.Message
                }
            };
        }
    }
} 