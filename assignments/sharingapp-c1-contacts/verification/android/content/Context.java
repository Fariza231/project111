package android.content;
import java.io.*;
/** Minimal filesystem test double, not an Android runtime or UI emulator. */
public class Context {
    public static final int MODE_PRIVATE = 0;
    private final File directory;
    public Context(File directory) { this.directory = directory; }
    public FileInputStream openFileInput(String name) throws FileNotFoundException {
        return new FileInputStream(new File(directory, name));
    }
    public FileOutputStream openFileOutput(String name, int mode) throws FileNotFoundException {
        return new FileOutputStream(new File(directory, name));
    }
}
