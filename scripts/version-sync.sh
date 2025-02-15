#!/bin/bash
function usage {
    echo "Usage: $(basename "$0") [-c] [-d SOURCE_DIR]" 2>&1
    echo 'Synchronize __version__.py to latest version in CHANGELOG.md'
    echo '   -d SOURCE_DIR   Specify location of __version__.py file.'
    echo '   -c              Compare versions and output proposed changes without changing anything.'
}


CHECK=0
SOURCE_DIR="."
while getopts ":hcd:" opt; do
    case $opt in
        h)
            usage
            exit 0
            ;;
        c)
            CHECK=1
            ;;
        d)
            SOURCE_DIR=$OPTARG
            ;;
        \?)
            echo "Invalid option: -$OPTARG." >&2
            usage
            exit 1
            ;;
    esac
done

# Version appearing earliest in CHANGELOGFILE will be used as ground truth.
CHANGELOGFILE="CHANGELOG.md"
VERSIONFILE="${SOURCE_DIR}/__version__.py"
RE_SEMVER_FULL="(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)(\.(0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?(\+([0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*))?"
# Pull out semver appearing earliest in CHANGELOGFILE.
LAST_VERSION=$(grep -o -m 1 -E "${RE_SEMVER_FULL}" "$CHANGELOGFILE")

if [ -z "$LAST_VERSION" ];
then
    # No match to semver regex in CHANGELOGFILE, so no version to go from.
    printf "Error: Unable to find latest version from %s.\n" "$CHANGELOGFILE"
    exit 1
fi

# Add files to this array that need to be kept in sync.
FILES_TO_CHANGE=("$VERSIONFILE")
# Add patterns to this array to be matched in the above files.
RE_SEMVERS=("$RE_SEMVER_FULL")
# Add versions to this array to be used as replacements for the patterns matched above from the corresponding files.
UPDATED_VERSIONS=("$LAST_VERSION")

for i in "${!FILES_TO_CHANGE[@]}"; do
    FILE_TO_CHANGE=${FILES_TO_CHANGE[$i]}
    RE_SEMVER=${RE_SEMVERS[$i]}
    UPDATED_VERSION=${UPDATED_VERSIONS[$i]}
    FILE_VERSION=$(grep -o -m 1 -E "${RE_SEMVER}" "$FILE_TO_CHANGE")
    if [ -z "$FILE_VERSION" ];
    then
        # No match to semver regex in VERSIONFILE, so nothing to replace
        printf "Error: No semver version found in file %s.\n" "$FILE_TO_CHANGE"
        exit 1
    else
        # Replace semver in VERSIONFILE with semver obtained from CHANGELOGFILE
        TMPFILE=$(mktemp /tmp/new_version.XXXXXX)
        # Check sed version, exit if version < 4.3
        if ! sed --version > /dev/null 2>&1; then
            CURRENT_VERSION=1.archaic
        else
            CURRENT_VERSION=$(sed --version | head -n1 | cut -d" " -f4)
        fi
        REQUIRED_VERSION="4.3"
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$CURRENT_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
            echo "sed version must be >= ${REQUIRED_VERSION}" && exit 1
        fi
        sed -r "s/$RE_SEMVER/$UPDATED_VERSION/" "$FILE_TO_CHANGE" > "$TMPFILE"
        if [ $CHECK == 1 ];
        then
            DIFF=$(diff "$FILE_TO_CHANGE"  "$TMPFILE" )
            if [ -z "$DIFF" ];
            then
                printf "version sync would make no changes.\n"
                rm "$TMPFILE"
                exit 0
            else
                printf "version sync would make the following changes:\n%s\n" "$DIFF"
                rm "$TMPFILE"
                exit 1
            fi
        else
            cp "$TMPFILE" "$FILE_TO_CHANGE" 
            rm "$TMPFILE"
        fi
    fi
done
