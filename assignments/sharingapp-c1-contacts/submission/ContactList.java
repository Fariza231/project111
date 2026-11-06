package com.example.sharingapp;

import android.content.Context;
import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import com.google.gson.reflect.TypeToken;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.reflect.Type;
import java.util.ArrayList;

/** Contact collection and app-private JSON persistence, analogous to ItemList. */
public class ContactList {
    private ArrayList<Contact> contacts;
    private String FILENAME = "contacts.sav";

    public ContactList() { contacts = new ArrayList<Contact>(); }

    public void setContacts(ArrayList<Contact> contact_list) {
        contacts = contact_list == null ? new ArrayList<Contact>() : contact_list;
    }
    public ArrayList<Contact> getContacts() { return contacts; }
    public void addContact(Contact contact) { contacts.add(contact); }
    public void deleteContact(Contact contact) {
        int index = getIndex(contact);
        if (index >= 0) { contacts.remove(index); }
    }
    public Contact getContact(int index) { return contacts.get(index); }
    public int getIndex(Contact contact) {
        if (contact == null || contact.getId() == null) { return -1; }
        for (int index = 0; index < contacts.size(); index++) {
            Contact candidate = contacts.get(index);
            if (candidate != null && contact.getId().equals(candidate.getId())) {
                return index;
            }
        }
        return -1;
    }
    public int getSize() { return contacts.size(); }
    public boolean hasContact(Contact contact) { return getIndex(contact) >= 0; }
    public boolean isUsernameAvailable(String username) {
        return getContactByUsername(username) == null;
    }
    public Contact getContactByUsername(String username) {
        if (username == null) { return null; }
        for (Contact contact : contacts) {
            if (contact != null && username.equals(contact.getUsername())) {
                return contact;
            }
        }
        return null;
    }
    public ArrayList<String> getAllUsernames() {
        ArrayList<String> usernames = new ArrayList<String>();
        for (Contact contact : contacts) {
            if (contact != null) { usernames.add(contact.getUsername()); }
        }
        return usernames;
    }
    public void loadContacts(Context context) {
        try (InputStreamReader reader = new InputStreamReader(
                context.openFileInput(FILENAME), "UTF-8")) {
            Type type = new TypeToken<ArrayList<Contact>>() {}.getType();
            ArrayList<Contact> loaded = new Gson().fromJson(reader, type);
            setContacts(loaded);
        } catch (FileNotFoundException missing) {
            contacts = new ArrayList<Contact>();
        } catch (IOException | JsonParseException invalid) {
            contacts = new ArrayList<Contact>();
        }
    }
    public void saveContacts(Context context) {
        try (OutputStreamWriter writer = new OutputStreamWriter(
                context.openFileOutput(FILENAME, Context.MODE_PRIVATE), "UTF-8")) {
            new Gson().toJson(contacts, writer);
        } catch (IOException error) {
            throw new IllegalStateException("Unable to save contacts", error);
        }
    }
}
