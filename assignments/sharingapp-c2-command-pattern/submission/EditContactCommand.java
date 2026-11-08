package com.example.sharingapp;

import android.content.Context;

/** Encapsulates the edit-contact request and its receiver. */
public class EditContactCommand extends Command {
    private ContactList contact_list;
    private Contact old_contact;
    private Contact new_contact;
    private Context context;

    public EditContactCommand(ContactList contact_list, Contact old_contact, Contact new_contact, Context context) {
        this.contact_list = contact_list;
        this.old_contact = old_contact;
        this.new_contact = new_contact;
        this.context = context;
    }

    @Override
    public void execute() {
        setIsExecuted(false);
        contact_list.deleteContact(old_contact);
        contact_list.addContact(new_contact);
        contact_list.saveContacts(context);
        // The supplied receiver returns void; this flag records normal completion.
        setIsExecuted(true);
    }
}
