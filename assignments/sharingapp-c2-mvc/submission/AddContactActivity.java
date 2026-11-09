package com.example.sharingapp;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

/** Contact form view: reads widgets, forwards actions and renders model notifications. */
public class AddContactActivity extends AppCompatActivity implements Contact.Observer {
    private EditText username;
    private EditText email;
    private ContactController contact_controller;
    private ContactListController contact_list_controller;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state); setContentView(R.layout.activity_add_contact);
        username = (EditText) findViewById(R.id.username);
        email = (EditText) findViewById(R.id.email);
        contact_list_controller = new ContactListController(getApplicationContext());
        contact_list_controller.loadContacts();
        contact_controller = new ContactController(new Contact("", "", null));
    }
    @Override protected void onStart() {
        super.onStart();
        if (contact_controller != null) {
            contact_controller.getContact().addObserver(this);
            render(contact_controller.getContact());
        }
    }
    @Override protected void onStop() {
        if (contact_controller != null) { contact_controller.getContact().removeObserver(this); }
        super.onStop();
    }
    public void saveContact(View view) {
        if (isFinishing()) { return; }
        try {
            contact_controller.updateContact(username.getText().toString(), email.getText().toString());
            if (contact_list_controller.addContact(contact_controller.getContact())) { finish(); }
            else { Toast.makeText(this, "Unable to save contact. Please retry.", Toast.LENGTH_LONG).show(); }
        } catch (ContactController.ValidationException error) { showError(error); }
    }
    private void showError(ContactController.ValidationException error) {
        if ("username".equals(error.getField())) { username.setError(error.getMessage()); }
        else if ("email".equals(error.getField())) { email.setError(error.getMessage()); }
        else { Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show(); }
    }
    private void render(Contact contact) {
        if (!username.getText().toString().equals(contact.getUsername())) { username.setText(contact.getUsername()); }
        if (!email.getText().toString().equals(contact.getEmail())) { email.setText(contact.getEmail()); }
    }
    @Override public void onContactChanged(final Contact contact) {
        runOnUiThread(new Runnable() { @Override public void run() { render(contact); } });
    }
}
