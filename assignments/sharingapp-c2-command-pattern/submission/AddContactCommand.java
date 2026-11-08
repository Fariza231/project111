package com.example.sharingapp;

import android.content.Context;

/** Encapsulates the add-contact request and its receiver. */
public class AddContactCommand extends Command {
    private ContactList contact_list;
    private Contact contact;
    private Context context;

    public AddContactCommand(ContactList contact_list, Contact contact, Context context) {
        this.contact_list = contact_list;
        this.contact = contact;
        this.context = context;
    }

    @Override
    public void execute() {
        setIsExecuted(false);
        contact_list.addContact(contact);
        contact_list.saveContacts(context);
        // The supplied receiver returns void; this flag records normal completion.
        setIsExecuted(true);
    }
}
