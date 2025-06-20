using WinGetMcpServer.Models;

namespace WinGetMcpServer.Services;

/// <summary>
/// Abstraction for WinGet operations using native .NET APIs
/// </summary>
public interface IWinGetService
{
    /// <summary>
    /// Search for packages in WinGet repositories
    /// </summary>
    Task<SearchResult> SearchPackagesAsync(string query, int maxResults = 10, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get detailed information about a specific package
    /// </summary>
    Task<PackageInfo?> GetPackageInfoAsync(string packageId, CancellationToken cancellationToken = default);

    /// <summary>
    /// List installed packages
    /// </summary>
    Task<List<PackageInfo>> ListInstalledPackagesAsync(int maxResults = 20, CancellationToken cancellationToken = default);

    /// <summary>
    /// Install a package (if installation is enabled)
    /// </summary>
    Task<InstallResult> InstallPackageAsync(string packageId, string? version = null, bool silent = true, CancellationToken cancellationToken = default);

    /// <summary>
    /// Check if WinGet APIs are available
    /// </summary>
    Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default);
} 