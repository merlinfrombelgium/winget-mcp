namespace WinGetMcpServer.Models;

/// <summary>
/// Represents package information from WinGet operations
/// </summary>
public class PackageInfo
{
    public required string Id { get; set; }
    public required string Name { get; set; }
    public required string Version { get; set; }
    public string? Publisher { get; set; }
    public string? Description { get; set; }
    public string? Source { get; set; }
    public bool IsInstalled { get; set; }
    public string? AvailableVersion { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
} 