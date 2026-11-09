package com.example.sharingapp;

/** Controls a contact form's working model. No widgets or Activity lifecycle dependencies. */
public class ContactController {
    public static class ValidationException extends IllegalArgumentException {
        private final String field;
        public ValidationException(String field, String message) { super(message); this.field = field; }
        public String getField() { return field; }
    }
    private final Contact contact;
    public ContactController(Contact contact) {
        if (contact == null) { throw new IllegalArgumentException("Contact is required"); }
        this.contact = contact;
    }
    public Contact getContact() { return contact; }
    public void setUsername(String username) { contact.setUsername(username); }
    public void setEmail(String email) { contact.setEmail(email); }
    public void updateContact(String username, String email) {
        validate(username, email);
        contact.update(username.trim(), email.trim());
    }
    public static void validate(String username, String email) {
        if (username == null || username.trim().isEmpty()) {
            throw new ValidationException("username", "Empty field!");
        }
        if (email == null || email.trim().isEmpty()) { throw new ValidationException("email", "Empty field!"); }
        if (!email.trim().contains("@")) { throw new ValidationException("email", "Must be an email address!"); }
    }
}
