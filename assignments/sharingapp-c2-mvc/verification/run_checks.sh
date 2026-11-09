#!/usr/bin/env bash
set -euo pipefail
verification_dir="$(cd "$(dirname "$0")" && pwd)"
: "${PROJECT_DIR:?Set PROJECT_DIR to the extracted full SharingApp project directory}"
: "${ANDROID_JAR:?Set ANDROID_JAR to an installed Android platform android.jar}"
java_dir="$PROJECT_DIR/app/src/main/java/com/example/sharingapp"
gson_jar="$PROJECT_DIR/app/src/include/gson-2.8.2-SNAPSHOT.jar"
classes_dir="$(mktemp -d)"
trap 'rm -rf "$classes_dir"' EXIT
sources=()
for name in Command Contact ContactList ContactController ContactListController Item ItemList ItemController ItemListController Dimensions AddContactCommand EditContactCommand DeleteContactCommand AddItemCommand EditItemCommand DeleteItemCommand; do
    sources+=("$java_dir/$name.java")
done
javac -d "$classes_dir" -cp "$ANDROID_JAR:$gson_jar" "$verification_dir/android/content/Context.java" "$verification_dir/MvcChecks.java" "${sources[@]}"
java -cp "$classes_dir:$ANDROID_JAR:$gson_jar" com.example.sharingapp.MvcChecks
