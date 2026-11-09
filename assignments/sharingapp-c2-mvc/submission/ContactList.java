package com.example.sharingapp;

import android.content.Context;
import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.gson.reflect.TypeToken;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.reflect.Type;
import java.util.ArrayList;

/** Observable contact collection; persistence remains compatible with the supplied commands. */
public class ContactList implements Contact.Observer {
    public interface Observer { void onContactsChanged(ContactList contacts); }
    private ArrayList<Contact> contacts = new ArrayList<Contact>();
    private String FILENAME = "contacts.sav";
    private transient ArrayList<Observer> observers;

    public ContactList() { }
    public void setContacts(ArrayList<Contact> values) {
        for (Contact contact : contacts) { contact.removeObserver(this); }
        contacts = new ArrayList<Contact>();
        if (values != null) {
            for (Contact contact : values) {
                if (contact != null) { contacts.add(contact); contact.addObserver(this); }
            }
        }
        notifyObservers();
    }
    public ArrayList<Contact> getContacts() { return new ArrayList<Contact>(contacts); }
    public ArrayList<String> getAllUsernames() {
        ArrayList<String> result = new ArrayList<String>();
        for (Contact contact : contacts) { result.add(contact.getUsername()); }
        return result;
    }
    public void addContact(Contact contact) {
        if (contact == null) { throw new IllegalArgumentException("Contact is required"); }
        if (hasContact(contact)) { throw new IllegalArgumentException("Contact ID already exists"); }
        contacts.add(contact); contact.addObserver(this); notifyObservers();
    }
    public void deleteContact(Contact contact) {
        int index = getIndex(contact);
        if (index >= 0) { contacts.remove(index).removeObserver(this); notifyObservers(); }
    }
    public Contact getContact(int index) { return contacts.get(index); }
    public int getSize() { return contacts.size(); }
    public int getIndex(Contact contact) {
        if (contact == null || contact.getId() == null) { return -1; }
        for (int i = 0; i < contacts.size(); i++) {
            if (contact.getId().equals(contacts.get(i).getId())) { return i; }
        }
        return -1;
    }
    public boolean hasContact(Contact contact) { return getIndex(contact) >= 0; }
    public Contact getContactByUsername(String username) {
        for (Contact contact : contacts) {
            if (username != null && username.equals(contact.getUsername())) { return contact; }
        }
        return null;
    }
    public boolean isUsernameAvailable(String username) { return getContactByUsername(username) == null; }
    public void loadContacts(Context context) {
        try (InputStreamReader reader = new InputStreamReader(context.openFileInput(FILENAME), "UTF-8")) {
            Type type = new TypeToken<ArrayList<Contact>>() {}.getType();
            ArrayList<Contact> loaded = new Gson().fromJson(reader, type);
            setContacts(loaded);
        } catch (IOException | JsonParseException error) {
            setContacts(new ArrayList<Contact>());
        }
    }
    /** Write a temporary file first so a failed save does not truncate the committed file. */
    public boolean saveContacts(Context context) {
        File temporary = context.getFileStreamPath(FILENAME + ".tmp");
        try {
            try (OutputStreamWriter writer = new OutputStreamWriter(
                    context.openFileOutput(FILENAME + ".tmp", Context.MODE_PRIVATE), "UTF-8")) {
                new Gson().toJson(contacts, writer);
            }
            return temporary.renameTo(context.getFileStreamPath(FILENAME));
        } catch (IOException error) { return false; }
        finally { if (temporary.exists()) { temporary.delete(); } }
    }
    public void addObserver(Observer observer) {
        if (observers == null) { observers = new ArrayList<Observer>(); }
        if (observer != null && !observers.contains(observer)) { observers.add(observer); }
    }
    public void removeObserver(Observer observer) {
        if (observers != null) { observers.remove(observer); }
    }
    public void notifyObservers() {
        if (observers != null) {
            for (Observer observer : new ArrayList<Observer>(observers)) { observer.onContactsChanged(this); }
        }
    }
    @Override public void onContactChanged(Contact contact) { notifyObservers(); }
}
