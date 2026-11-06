#!/usr/bin/env bash
set -euo pipefail
verification_dir="$(cd "$(dirname "$0")" && pwd)"
assignment_dir="$(dirname "$verification_dir")"
: "${GSON_JAR:?Set GSON_JAR to SharingApp/app/src/include/gson-2.8.2-SNAPSHOT.jar from the project ZIP}"
classes_dir="$(mktemp -d)"
trap 'rm -rf "$classes_dir"' EXIT
javac -d "$classes_dir" -cp "$GSON_JAR" "$verification_dir/android/content/Context.java" "$verification_dir/ContactModelCheck.java" "$assignment_dir/submission/Contact.java" "$assignment_dir/submission/ContactList.java"
java -cp "$classes_dir:$GSON_JAR" ContactModelCheck
