package com.example.sharingapp;
import android.content.Context;
import com.example.sharingapp.*;
import java.nio.file.*;
import java.util.*;

/** Checks the submitted commands against the starter's real ContactList and Gson persistence. */
public class ContactCommandsCheck {
    static int count;
    static void check(boolean result, String label) {
        if (!result) throw new AssertionError(label);
        count++; System.out.println("PASS " + label);
    }
    static class Receiver extends ContactList {
        final ArrayList<String> events = new ArrayList<String>();
        boolean failSaving;
        @Override public void addContact(Contact c) { events.add("add:"+c.getUsername()); super.addContact(c); }
        @Override public void deleteContact(Contact c) { events.add("delete:"+c.getUsername()); super.deleteContact(c); }
        @Override public void saveContacts(Context c) {
            events.add("save");
            if (failSaving) throw new IllegalStateException("Injected receiver failure");
            super.saveContacts(c);
        }
    }
    public static void main(String[] args) throws Exception {
        Path directory = Files.createTempDirectory("command-pattern-check");
        Context context = new Context(directory.toFile()); Receiver receiver = new Receiver();
        Contact alice = new Contact("alice","alice@example.com",null);
        Command add = new AddContactCommand(receiver,alice,context);
        check(!add.isExecuted(),"add starts unexecuted");
        check(receiver.getSize()==0 && receiver.events.isEmpty(),"add construction has no receiver effects");
        add.execute();
        check(add.isExecuted(),"add marks normal completion");
        check(receiver.events.equals(Arrays.asList("add:alice","save")),"add delegates mutation then persistence exactly once");
        check(receiver.getSize()==1 && receiver.getContact(0)==alice,"add uses supplied receiver and contact");
        receiver.loadContacts(context);
        check(receiver.getSize()==1 && receiver.getContact(0).getId().equals(alice.getId()),"added contact survives JSON reload");
        Contact old = receiver.getContact(0);
        Contact updated = new Contact("alice","changed@example.com",old.getId());
        receiver.events.clear();
        Command edit = new EditContactCommand(receiver,old,updated,context);
        check(!edit.isExecuted(),"edit starts unexecuted");
        check(receiver.events.isEmpty() && receiver.getContact(0)==old,"edit construction leaves original intact");
        edit.execute();
        check(edit.isExecuted(),"edit marks normal completion");
        check(receiver.events.equals(Arrays.asList("delete:alice","add:alice","save")),"edit delegates delete, add and one save in order");
        check(receiver.getSize()==1 && receiver.getContact(0)==updated,"edit replaces original without adding a second record");
        check(receiver.getContact(0).getId().equals(alice.getId()),"edited contact retains its identifier");
        receiver.loadContacts(context);
        check(receiver.getContact(0).getEmail().equals("changed@example.com"),"email edit survives JSON reload");
        Contact bob = new Contact("bob","bob@example.com",null);
        new AddContactCommand(receiver,bob,context).execute();receiver.events.clear();
        Command delete = new DeleteContactCommand(receiver,bob,context);
        check(!delete.isExecuted(),"delete starts unexecuted");
        check(receiver.getSize()==2 && receiver.events.isEmpty(),"delete construction has no receiver effects");
        delete.execute();
        check(delete.isExecuted(),"delete marks normal completion");
        check(receiver.events.equals(Arrays.asList("delete:bob","save")),"delete delegates removal then one save");
        check(receiver.getSize()==1 && receiver.getContactByUsername("alice")!=null,"delete preserves unrelated contacts");
        receiver.loadContacts(context);
        check(receiver.getContactByUsername("bob")==null && receiver.getSize()==1,"deletion survives JSON reload");
        for (int type=0;type<3;type++) {
            Receiver failing = new Receiver(); Contact c = new Contact("test","t@e",null);
            failing.addContact(c);failing.events.clear();
            Command command = type==0?new AddContactCommand(failing,c,context):type==1?new DeleteContactCommand(failing,c,context):new EditContactCommand(failing,c,new Contact("next","n@e",c.getId()),context);
            command.setIsExecuted(true);failing.failSaving=true;
            boolean thrown=false;
            try { command.execute(); } catch (IllegalStateException expected) { thrown=true; }
            check(thrown,"command "+type+" propagates receiver runtime failure");
            check(!command.isExecuted(),"command "+type+" clears stale success before failed execution");
        }
        System.out.println("RESULT: "+count+" checks passed. Real starter ContactList; filesystem Context test double; no Android UI execution.");
    }
}
