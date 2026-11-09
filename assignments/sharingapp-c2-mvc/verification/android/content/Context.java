package android.content;
import java.io.*;
/** Filesystem test double, not an Android runtime. */
public class Context {
    public static final int MODE_PRIVATE = 0;
    private final File directory;
    private boolean failWrites;
    public Context(File directory) { this.directory = directory; }
    public void setFailWrites(boolean value) { failWrites = value; }
    public File getFileStreamPath(String name) { return new File(directory, name); }
    public FileInputStream openFileInput(String name) throws FileNotFoundException {
        return new FileInputStream(getFileStreamPath(name));
    }
    public FileOutputStream openFileOutput(String name, int mode) throws FileNotFoundException {
        if (failWrites) { throw new FileNotFoundException("Injected write failure"); }
        return new FileOutputStream(getFileStreamPath(name));
    }
}
