using Microsoft.Extensions.Logging;
using WinGetMcpServer.Models;
using WinGetMcpServer.Services;

namespace WinGetMcpServer.Tools;

/// <summary>
/// MCP tool for searching WinGet packages
/// </summary>
public class SearchTool : WinGetToolBase
{
    public SearchTool(IWinGetService winGetService, ILogger<SearchTool> logger) 
        : base(winGetService, logger)
    {
    }

    /// <summary>
    /// Execute package search with the given request
    /// </summary>
    public async Task<object> ExecuteAsync(SearchRequest request, CancellationToken cancellationToken = default)
    {
        try
        {
            ValidateInput(request);
            ValidateSearchRequest(request);

            _logger.LogInformation("Executing search for query: {Query}", request.Query);

            var result = await _winGetService.SearchPackagesAsync(
                request.Query, 
                request.Limit ?? 10, 
                cancellationToken);

            var response = new
            {
                query = request.Query,
                totalFound = result.TotalFound,
                returned = result.Returned,
                hasMore = result.HasMore,
                executionTime = result.ExecutionTime.TotalMilliseconds,
                packages = result.Packages.Select(p => new
                {
                    id = p.Id,
                    name = p.Name,
                    version = p.Version,
                    publisher = p.Publisher,
                    description = p.Description?.Substring(0, Math.Min(p.Description.Length, 200)) + 
                                  (p.Description?.Length > 200 ? "..." : ""),
                    source = p.Source
                })
            };

            return CreateSuccessResponse(response, "search");
        }
        catch (Exception ex)
        {
            return HandleException(ex, "search");
        }
    }

    /// <summary>
    /// Validate search-specific parameters
    /// </summary>
    private void ValidateSearchRequest(SearchRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Query))
            throw new ValidationException(nameof(request.Query), 
                "Search query cannot be empty", 
                "Query parameter is null or whitespace");

        if (request.Limit.HasValue && request.Limit.Value <= 0)
            throw new ValidationException(nameof(request.Limit), 
                "Limit must be greater than 0", 
                $"Limit value is {request.Limit.Value}");

        if (request.Limit.HasValue && request.Limit.Value > 50)
            throw new ValidationException(nameof(request.Limit), 
                "Limit cannot exceed 50 for performance reasons", 
                $"Limit value is {request.Limit.Value}");
    }
}

/// <summary>
/// Search request model
/// </summary>
public class SearchRequest
{
    public required string Query { get; set; }
    public int? Limit { get; set; }
    public string? Source { get; set; }
} 