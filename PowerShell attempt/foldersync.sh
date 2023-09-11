#!/bin/bash

sourcePath=$1
replicaPath=$2
logFilePath=$3

# Function to synchronize folders
sync_folders() {
    local source=$1
    local destination=$2
    local logFile=$3
    
    IFS=$'\n'
    
    sourceFiles=($(find "$source" -type f))
    destinationFiles=($(find "$destination" -type f))
    
    for srcFile in "${sourceFiles[@]}"; do
        destFile="${srcFile/$source/$destination}"
        
        if [[ ! -f $destFile ]]; then
            mkdir -p "$(dirname "$destFile")"
            cp "$srcFile" "$destFile"
            echo "Copied $srcFile to $destFile" >> "$logFile"
        else
            srcModTime=$(stat -c %Y "$srcFile")
            destModTime=$(stat -c %Y "$destFile")
            
            if (( srcModTime > destModTime )); then
                cp "$srcFile" "$destFile"
                echo "Updated $srcFile in $destFile" >> "$logFile"
            fi
        fi
    done
    
    for destFile in "${destinationFiles[@]}"; do
        srcFile="${destFile/$destination/$source}"
        
        if [[ ! -f $srcFile ]]; then
            rm "$destFile"
            echo "Removed $destFile" >> "$logFile"
        fi
    done
}

# Main script logic
if sync_folders "$sourcePath" "$replicaPath" "$logFilePath"; then
    echo "Synchronization completed successfully!"
else
    echo "An error occurred: $?" >&2
fi
