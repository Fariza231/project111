package com.example.sharingapp;

import android.content.Context;
import java.util.ArrayList;

/** Coordinates validation, commands and persistence for the contact collection. */
public class ContactListController {
    private final ContactList contact_list;
    private final Context context;
    public ContactListController(ContactList contact_list, Context context) {
        if (contact_list == null || context == null) { throw new IllegalArgumentException("Model and context are required"); }
        this.contact_list = contact_list;
        this.context = context;
    }
    public ContactListController(Context context) { this(new ContactList(), context); }
    public ContactList getContactList() { return contact_list; }
    public Contact getContact(int index) { return contact_list.getContact(index); }
    public int getSize() { return contact_list.getSize(); }
    public void loadContacts() { contact_list.loadContacts(context); }
    public boolean saveContacts() { return contact_list.saveContacts(context); }
    public ArrayList<String> getAllUsernames() { return contact_list.getAllUsernames(); }
    public Contact getContactByUsername(String username) { return contact_list.getContactByUsername(username); }
    public boolean isUsernameAvailable(String username) { return contact_list.isUsernameAvailable(username); }

    private void validate(Contact contact, String originalId) {
        if (contact == null) { throw new IllegalArgumentException("Contact is required"); }
        ContactController.validate(contact.getUsername(), contact.getEmail());
        Contact conflict = contact_list.getContactByUsername(contact.getUsername());
        if (conflict != null && !conflict.getId().equals(originalId)) {
            throw new ContactController.ValidationException("username", "Username already taken!");
        }
    }
    public void requireBorrowerOptions() {
        if (getSize() == 0) {
            throw new ContactController.ValidationException("borrower", "Add a contact before borrowing an item.");
        }
    }
    public boolean isActiveBorrower(Contact contact) {
        ItemList items = new ItemList(); items.loadItems(context);
        for (Contact borrower : items.getActiveBorrowers()) {
            if (contact != null && contact.getId().equals(borrower.getId())) { return true; }
        }
        return false;
    }
    private void requireEditable(Contact contact) {
        if (isActiveBorrower(contact)) {
            throw new ContactController.ValidationException("contact", "Cannot edit or delete active borrower!");
        }
    }
    private boolean execute(Command command) {
        ArrayList<Contact> before = contact_list.getContacts();
        try {
            command.execute();
            if (command.isExecuted()) { return true; }
        } catch (RuntimeException error) {
            contact_list.setContacts(before); throw error;
        }
        contact_list.setContacts(before);
        return false;
    }
    public boolean addContact(Contact contact) {
        validate(contact, null);
        return execute(new AddContactCommand(contact_list, contact, context));
    }
    public boolean editContact(Contact original, Contact replacement) {
        int index = contact_list.getIndex(original);
        if (index < 0 || replacement == null || !original.getId().equals(replacement.getId())) {
            throw new IllegalArgumentException("Edit must retain an existing contact ID");
        }
        requireEditable(original); validate(replacement, original.getId());
        return execute(new EditContactCommand(contact_list, contact_list.getContact(index), replacement, context));
    }
    public boolean deleteContact(Contact contact) {
        int index = contact_list.getIndex(contact);
        if (index < 0) { return false; }
        requireEditable(contact);
        return execute(new DeleteContactCommand(contact_list, contact_list.getContact(index), context));
    }
}
