package com.example.sharingapp;

import android.content.Intent;
import android.graphics.Rect;
import android.os.SystemClock;
import android.support.test.InstrumentationRegistry;
import android.support.test.runner.AndroidJUnit4;
import android.support.test.uiautomator.By;
import android.support.test.uiautomator.BySelector;
import android.support.test.uiautomator.UiDevice;
import android.support.test.uiautomator.UiObject2;
import android.support.test.uiautomator.Until;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.io.File;
import java.util.regex.Pattern;
import static org.junit.Assert.*;

/** Performs the assignment's actual on-device UI walkthrough, starting with fresh app data. */
@RunWith(AndroidJUnit4.class)
public class ContactsWalkthroughTest {
    private UiDevice device;
    private final String pkg = "com.example.sharingapp";
    private UiObject2 visible(BySelector selector) {
        UiObject2 object = device.wait(Until.findObject(selector), 20000);
        if (object == null) {
            File directory = InstrumentationRegistry.getTargetContext().getExternalFilesDir(null);
            device.takeScreenshot(new File(directory, "failure.png"));
            try { device.dumpWindowHierarchy(new File(directory, "failure.xml")); } catch (Exception ignored) { }
        }
        assertNotNull("Missing UI element: " + selector, object);
        return object;
    }
    private UiObject2 res(String id) { return visible(By.res(pkg, id)); }
    private void click(String id) { res(id).click(); SystemClock.sleep(500); }
    private void fill(String id, String text) { res(id).setText(text); }
    private void shot(String name) {
        SystemClock.sleep(800);
        device.takeScreenshot(new File(InstrumentationRegistry.getTargetContext().getExternalFilesDir(null), name + ".png"));
        System.out.println("PASS " + name);
    }
    private void longPress(BySelector selector) {
        Rect bounds = visible(selector).getVisibleBounds();
        device.swipe(bounds.centerX(), bounds.centerY(), bounds.centerX(), bounds.centerY(), 240);
        SystemClock.sleep(1000);
    }
    private void addContact(String username) {
        click("imageButton"); fill("username", username); fill("email", username + "@example.com");
        click("save_button"); visible(By.text("Username: " + username)); shot("added_" + username);
    }
    @Test
    public void contactsAndBorrowerWalkthrough() {
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        Intent launch = InstrumentationRegistry.getTargetContext().getPackageManager().getLaunchIntentForPackage(pkg);
        launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        InstrumentationRegistry.getTargetContext().startActivity(launch);
        visible(By.res(pkg, "toolbar")); shot("01_main");
        device.pressMenu(); visible(By.text("Contacts")).clickAndWait(Until.newWindow(), 15000); visible(By.res(pkg, "imageButton")); shot("02_contacts");
        addContact("alice"); addContact("bob"); addContact("charlie");
        longPress(By.text("Username: alice")); fill("email", "alice.updated@example.com");
        click("save_edited_user_button"); visible(By.text("Email: alice.updated@example.com")); shot("03_email_updated");
        longPress(By.text("Username: charlie")); click("delete_edited_user_button");
        visible(By.res(pkg, "my_contacts")); assertNull(device.findObject(By.text("Username: charlie"))); shot("04_contact_deleted");
        device.pressBack(); visible(By.res(pkg, "toolbar"));
        visible(By.text(Pattern.compile("(?i)available"))).click(); shot("05_available_inventory");
        click("imageButton"); fill("title", "Camera"); fill("maker", "Canon"); fill("description", "Digital camera");
        fill("length", "12"); fill("width", "8"); fill("height", "7");
        click("save_button"); visible(By.text("Title: Camera")); shot("06_item_added");
        longPress(By.text("Title: Camera")); click("available_switch");
        visible(By.text("alice")); shot("07_default_borrower");
        click("borrower_spinner"); visible(By.text("bob")).click(); visible(By.text("bob")); shot("08_selected_borrower");
        click("save_button"); visible(By.text("Title: Camera")); visible(By.text("Status: Borrowed")); shot("09_borrow_saved");
        longPress(By.text("Title: Camera")); visible(By.text("bob")); shot("10_borrower_persisted");
        device.pressBack(); visible(By.res(pkg, "toolbar"));
    }
}
