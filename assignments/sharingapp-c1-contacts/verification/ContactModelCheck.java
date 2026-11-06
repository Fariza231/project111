import com.example.sharingapp.Contact;
import com.example.sharingapp.ContactList;
import android.content.Context;
import java.nio.file.*;
import java.util.*;

public class ContactModelCheck {
    private static int passed;
    private static void check(boolean condition, String what) {
        if (!condition) { throw new AssertionError(what); }
        passed++; System.out.println("PASS " + what);
    }
    public static void main(String[] args) throws Exception {
        Contact first = new Contact("alice", "alice@example.com", null);
        Contact second = new Contact("bob", "bob@example.com", null);
        UUID.fromString(first.getId());
        check(!first.getId().equals(second.getId()), "new contacts have distinct UUIDs");
        Contact edited = new Contact("alice", "new@example.com", first.getId());
        check(first.getId().equals(edited.getId()), "editing preserves identity");
        edited.setUsername("alicia"); edited.setEmail("updated@example.com");
        check(edited.getUsername().equals("alicia") && edited.getEmail().equals("updated@example.com"), "getters and setters");
        edited.updateId("restored"); check(edited.getId().equals("restored"), "updateId preserves supplied identifier");
        ContactList list = new ContactList();
        check(list.getSize() == 0, "new list is empty");
        list.addContact(first); list.addContact(second);
        check(list.getSize() == 2 && list.getContact(1) == second, "add and indexed lookup");
        check(!list.isUsernameAvailable("alice") && list.isUsernameAvailable("carol"), "username uniqueness query");
        check(list.getContactByUsername("bob") == second && list.getContactByUsername("missing") == null, "username lookup and absent contact");
        check(list.getAllUsernames().equals(new ArrayList<String>(Arrays.asList("alice", "bob"))), "borrower spinner username order");
        Contact equivalent = new Contact("alice", "copy@example.com", first.getId());
        check(list.hasContact(equivalent) && list.getIndex(equivalent) == 0, "identity-based matching of separately loaded borrowers");
        check(!list.hasContact(null) && list.getIndex(new Contact("other", "x@y", null)) == -1, "missing identity lookup");
        ContactList active = new ContactList(); active.setContacts(new ArrayList<Contact>(Arrays.asList(equivalent)));
        check(list.getSize() == 2 && active.getSize() == 1, "active borrower collection does not replace main contacts");
        Path dir = Files.createTempDirectory("sharing-contacts-check"); Context context = new Context(dir.toFile());
        list.saveContacts(context); ContactList loaded = new ContactList(); loaded.loadContacts(context);
        check(loaded.getSize() == 2 && loaded.getContact(0).getId().equals(first.getId()), "JSON save and reload preserve identities and records");
        loaded.getContact(0).setEmail("edited@example.com"); loaded.saveContacts(context);
        ContactList reloaded = new ContactList(); reloaded.loadContacts(context);
        check(reloaded.getContactByUsername("alice").getEmail().equals("edited@example.com"), "email edit survives reopening");
        reloaded.deleteContact(equivalent); reloaded.saveContacts(context); loaded.loadContacts(context);
        check(loaded.getSize() == 1 && loaded.getContactByUsername("bob") != null, "identity-based delete survives reopening");
        loaded.deleteContact(equivalent); check(loaded.getSize() == 1, "deleting absent contact leaves others intact");
        loaded.addContact(new Contact("Жан", "jan@example.com", null)); loaded.saveContacts(context); loaded.loadContacts(context);
        check(loaded.getContactByUsername("Жан") != null, "UTF-8 contact persistence");
        Files.delete(dir.resolve("contacts.sav")); loaded.loadContacts(context);
        check(loaded.getSize() == 0, "first-run missing file loads empty list");
        Files.write(dir.resolve("contacts.sav"), "null".getBytes("UTF-8")); loaded.loadContacts(context);
        check(loaded.getSize() == 0, "JSON null does not create null collection");
        Files.write(dir.resolve("contacts.sav"), "not json".getBytes("UTF-8")); loaded.loadContacts(context);
        check(loaded.getSize() == 0, "malformed JSON does not crash loading");
        System.out.println("RESULT: " + passed + " checks passed; filesystem Context test double; no Android UI execution.");
    }
}
