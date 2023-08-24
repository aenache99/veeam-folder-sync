param (
    [string]$sourcePath,
    [string]$replicaPath,
    [string]$logFilePath
)

# Function to synchronize folders
function Sync-Folders {
    param (
        [string]$source,
        [string]$destination,
        [string]$logFile
    )

    $sourceFiles = Get-ChildItem -Path $source -File -Recurse
    $destinationFiles = Get-ChildItem -Path $destination -File -Recurse

    foreach ($file in $sourceFiles) {
        $destinationFile = $destinationFiles | Where-Object { $_.FullName -eq $file.FullName.Replace($source, $destination) }

        if ($destinationFile -eq $null) {
            Copy-Item -Path $file.FullName -Destination $file.FullName.Replace($source, $destination)
            Write-Output "Copied $($file.FullName) to $($file.FullName.Replace($source, $destination))" | Out-File -Append -FilePath $logFile
        } elseif ($file.LastWriteTime -gt $destinationFile.LastWriteTime) {
            Copy-Item -Path $file.FullName -Destination $file.FullName.Replace($source, $destination) -Force
            Write-Output "Updated $($file.FullName) in $($file.FullName.Replace($source, $destination))" | Out-File -Append -FilePath $logFile
        }
    }

    foreach ($file in $destinationFiles) {
        $sourceFile = $sourceFiles | Where-Object { $_.FullName -eq $file.FullName.Replace($destination, $source) }

        if ($sourceFile -eq $null) {
            Remove-Item -Path $file.FullName -Force
            Write-Output "Removed $($file.FullName)" | Out-File -Append -FilePath $logFile
        }
    }
}

# Main script logic
try {
    Sync-Folders -source $sourcePath -destination $replicaPath -logFile $logFilePath
    Write-Host "Synchronization completed successfully!"
} catch {
    Write-Host "An error occurred: $_" -ForegroundColor Red
}
