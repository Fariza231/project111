package com.example.sharingapp;

import android.content.Context;

/** Encapsulates the delete-contact request and its receiver. */
public class DeleteContactCommand extends Command {
    private ContactList contact_list;
    private Contact contact;
    private Context context;

    public DeleteContactCommand(ContactList contact_list, Contact contact, Context context) {
        this.contact_list = contact_list;
        this.contact = contact;
        this.context = context;
    }

    @Override
    public void execute() {
        setIsExecuted(false);
        contact_list.deleteContact(contact);
        contact_list.saveContacts(context);
        // The supplied receiver returns void; this flag records normal completion.
        setIsExecuted(true);
    }
}
