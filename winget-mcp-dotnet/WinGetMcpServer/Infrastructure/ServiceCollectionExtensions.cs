using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Caching.Memory;
using WinGetMcpServer.Configuration;
using WinGetMcpServer.Services;
using WinGetMcpServer.Tools;

namespace WinGetMcpServer.Infrastructure;

/// <summary>
/// Extension methods for configuring dependency injection
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// Add all WinGet MCP Server services to the dependency injection container
    /// </summary>
    public static IServiceCollection AddWinGetMcpServer(this IServiceCollection services, IConfiguration configuration)
    {
        // Configuration
        services.Configure<McpServerOptions>(configuration.GetSection(McpServerOptions.SectionName));

        // Core Services
        services.AddSingleton<IMemoryCache, MemoryCache>();
        services.AddSingleton<IWinGetService, WinGetService>();

        // Tools
        services.AddScoped<SearchTool>();

        // Logging
        services.AddLogging(builder =>
        {
            builder.AddConsole();
            builder.AddDebug();
            builder.SetMinimumLevel(LogLevel.Information);
        });

        return services;
    }

    /// <summary>
    /// Add MCP protocol services
    /// </summary>
    public static IServiceCollection AddMcpProtocol(this IServiceCollection services)
    {
        // MCP-specific services will be registered here
        // This will be expanded when we integrate the ModelContextProtocol SDK
        
        return services;
    }

    /// <summary>
    /// Validate service registration
    /// </summary>
    public static void ValidateServices(this IServiceProvider serviceProvider)
    {
        // Validate required services are registered
        var winGetService = serviceProvider.GetService<IWinGetService>();
        if (winGetService == null)
            throw new InvalidOperationException("IWinGetService is not registered");

        var searchTool = serviceProvider.GetService<SearchTool>();
        if (searchTool == null)
            throw new InvalidOperationException("SearchTool is not registered");

        var logger = serviceProvider.GetService<ILogger<Program>>();
        logger?.LogInformation("All required services validated successfully");
    }
} 