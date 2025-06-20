namespace WinGetMcpServer.Models;

/// <summary>
/// Represents the result of a package installation operation
/// </summary>
public class InstallResult
{
    public required string PackageId { get; set; }
    public string? Version { get; set; }
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public int ExitCode { get; set; }
    public TimeSpan ExecutionTime { get; set; }
    public bool RequiredRestart { get; set; }
    public Dictionary<string, object>? Details { get; set; }
} 