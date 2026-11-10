package com.example.sharingapp;

import android.content.Context;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;

/**
 * Add a new contact
 */
public class AddContactActivity extends AppCompatActivity {

    // Form values consumed only after validateInput() succeeds.
    private String username_str;
    private String email_str;


    private ContactList contact_list = new ContactList();
    private ContactListController contact_list_controller = new ContactListController(contact_list);

    private Context context;

    private EditText username;
    private EditText email;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_contact);

        username = (EditText) findViewById(R.id.username);
        email = (EditText) findViewById(R.id.email);

        context = getApplicationContext();
        contact_list_controller.loadContacts(context);
    }

    public void saveContact(View view) {

        if (!validateInput()) {
            return;
        }

        Contact contact = new Contact(username_str, email_str, null);

        // Add contact
        boolean success = contact_list_controller.addContact(contact, context);
        if (!success) {
            return;
        }

        // End AddContactActivity
        finish();
    }

    /** Read form values and preserve the original validation order and error messages. */
    private boolean validateInput() {

        username_str = username.getText().toString();
        email_str = email.getText().toString();

        if (username_str.equals("")) {
            username.setError("Empty field!");
            return false;
        }

        if (!email_str.contains("@")) {
            email.setError("Must be an email address!");
            return false;
        }

        if (!contact_list_controller.isUsernameAvailable(username_str)){
            username.setError("Username already taken!");
            return false;
        }
        return true;
    }
}
