using Microsoft.Extensions.Logging;
using WinGetMcpServer.Models;
using WinGetMcpServer.Services;

namespace WinGetMcpServer.Tools;

/// <summary>
/// Base class for all WinGet MCP tools providing common functionality
/// </summary>
public abstract class WinGetToolBase
{
    protected readonly IWinGetService _winGetService;
    protected readonly ILogger _logger;

    protected WinGetToolBase(IWinGetService winGetService, ILogger logger)
    {
        _winGetService = winGetService;
        _logger = logger;
    }

    /// <summary>
    /// Validate common input parameters
    /// </summary>
    protected virtual void ValidateInput(object request)
    {
        if (request == null)
            throw new ValidationException("request", "Request cannot be null", "Request parameter is null");
    }

    /// <summary>
    /// Handle exceptions and return structured error response
    /// </summary>
    protected virtual object HandleException(Exception ex, string operation)
    {
        _logger.LogError(ex, "Error in {Operation}: {Message}", operation, ex.Message);

        if (ex is WinGetMcpException wingetEx)
        {
            return new
            {
                success = false,
                error = wingetEx.UserMessage,
                category = wingetEx.Category.ToString(),
                details = wingetEx.Context
            };
        }

        return new
        {
            success = false,
            error = "An unexpected error occurred",
            category = "SystemError",
            details = new { message = ex.Message }
        };
    }

    /// <summary>
    /// Create a successful response with data
    /// </summary>
    protected virtual object CreateSuccessResponse(object data, string operation = "")
    {
        return new
        {
            success = true,
            operation = operation,
            data = data,
            timestamp = DateTime.UtcNow
        };
    }
} 