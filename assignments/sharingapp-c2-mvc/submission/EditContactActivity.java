package com.example.sharingapp;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

/** Edits a working copy; cancelling never changes the committed contact. */
public class EditContactActivity extends AppCompatActivity implements Contact.Observer {
    private EditText username;
    private EditText email;
    private Contact original;
    private ContactController contact_controller;
    private ContactListController contact_list_controller;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state); setContentView(R.layout.activity_edit_contact);
        username = (EditText) findViewById(R.id.username);
        email = (EditText) findViewById(R.id.email);
        contact_list_controller = new ContactListController(getApplicationContext());
        contact_list_controller.loadContacts();
        int position = getIntent().getIntExtra("position", -1);
        if (position < 0 || position >= contact_list_controller.getSize()) { finish(); return; }
        original = contact_list_controller.getContact(position);
        contact_controller = new ContactController(new Contact(original.getUsername(), original.getEmail(), original.getId()));
        if (contact_list_controller.isActiveBorrower(original)) {
            Toast.makeText(this, "Cannot edit or delete active borrower!", Toast.LENGTH_LONG).show(); finish();
        }
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
        if (contact_controller == null) { return; }
        try {
            contact_controller.updateContact(username.getText().toString(), email.getText().toString());
            if (contact_list_controller.editContact(original, contact_controller.getContact())) { finish(); }
            else { showStorageError(); }
        } catch (ContactController.ValidationException error) { showError(error); }
    }
    public void deleteContact(View view) {
        if (isFinishing()) { return; }
        if (original == null) { return; }
        try {
            if (contact_list_controller.deleteContact(original)) { finish(); }
            else { showStorageError(); }
        } catch (ContactController.ValidationException error) { showError(error); }
    }
    private void showStorageError() { Toast.makeText(this, "Unable to save contact. Please retry.", Toast.LENGTH_LONG).show(); }
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
