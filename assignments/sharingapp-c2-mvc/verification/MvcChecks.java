package com.example.sharingapp;
import android.content.Context;
import java.nio.file.*;
import java.util.*;

/** Executable contract checks against production MVC models/controllers and starter commands. */
public class MvcChecks {
    static int checks;
    static void check(boolean value,String name) {
        if(!value) throw new AssertionError(name);
        checks++;System.out.println("PASS "+name);
    }
    static void rejected(Runnable operation,String field,String name) {
        try { operation.run();throw new AssertionError(name); }
        catch(ContactController.ValidationException error) {check(field.equals(error.getField()),name);}
    }
    public static void main(String[] args) throws Exception {
        Path directory=Files.createTempDirectory("sharing-mvc-check");
        Context context=new Context(directory.toFile());
        Contact contact=new Contact("alice","a@example.com",null);
        UUID.fromString(contact.getId());
        check(contact.getId()!=null,"contact UUID generated");
        Contact copy=new Contact("alice","a@example.com",contact.getId());
        check(contact.getId().equals(copy.getId()),"contact ID reuse");
        final int[] updates={0};
        Contact.Observer view=new Contact.Observer(){public void onContactChanged(Contact c){updates[0]++;}};
        contact.addObserver(view);contact.addObserver(view);contact.setEmail("changed@example.com");
        check(updates[0]==1,"one model notification with duplicate subscription suppressed");
        contact.setEmail("changed@example.com");check(updates[0]==1,"unchanged value does not trigger render loop");
        contact.update("alicia","new@example.com");check(updates[0]==2,"coherent username/email update sends one notification");
        contact.removeObserver(view);contact.setEmail("again@example.com");check(updates[0]==2,"detached view is not notified");
        Contact.Observer selfRemoving=new Contact.Observer(){public void onContactChanged(Contact c){c.removeObserver(this);}};
        contact.addObserver(selfRemoving);contact.setEmail("one@example.com");contact.setEmail("two@example.com");
        check(true,"observer can detach during callback");
        ContactList model=new ContactList();final int[] collectionUpdates={0};
        ContactList.Observer listView=new ContactList.Observer(){public void onContactsChanged(ContactList c){collectionUpdates[0]++;}};
        model.addObserver(listView);model.addContact(contact);
        check(collectionUpdates[0]==1,"collection add notifies list view");
        contact.setEmail("list@example.com");check(collectionUpdates[0]==2,"child property change notifies collection observers");
        model.getContacts().clear();check(model.getSize()==1,"collection getter prevents unobserved list mutation");
        ContactList independent=new ContactList();independent.addContact(copy);
        check(model.getSize()==1,"separate model instances do not reset contact directory");
        model.deleteContact(copy);check(model.getSize()==0,"delete matches stable identity rather than reference");
        int previous=collectionUpdates[0];contact.setEmail("detached@example.com");
        check(previous==collectionUpdates[0],"removed child no longer notifies former collection");
        model.removeObserver(listView);model.addContact(contact);check(collectionUpdates[0]==previous,"collection view unsubscribe works");
        Contact draft=new Contact("", "", null);ContactController editor=new ContactController(draft);
        editor.updateContact("  alice  ","  alice@example.com  ");
        check(draft.getUsername().equals("alice") && draft.getEmail().equals("alice@example.com"),"form controller normalizes validated input");
        rejected(()->editor.updateContact(" ","a@b"),"username","blank username rejected in controller");
        rejected(()->editor.updateContact("alice",""),"email","blank email rejected in controller");
        rejected(()->editor.updateContact("alice","bad"),"email","invalid email rejected in controller");
        check(draft.getEmail().equals("alice@example.com"),"invalid input leaves model untouched");
        model=new ContactList();ContactListController controller=new ContactListController(model,context);
        controller.loadContacts();check(controller.getSize()==0,"first-run empty persistence loads safely");
        check(controller.addContact(draft),"controller executes add command and persists");
        ContactList reload=new ContactList();reload.loadContacts(context);
        check(reload.getSize()==1 && reload.getContact(0).getId().equals(draft.getId()),"added contact survives JSON reload");
        rejected(()->controller.addContact(new Contact("alice","other@example.com",null)),"username","duplicate username rejected before command");
        check(controller.getSize()==1,"rejected duplicate does not mutate directory");
        Contact original=controller.getContact(0);
        Contact working=new Contact(original.getUsername(),original.getEmail(),original.getId());
        new ContactController(working).updateContact("alice","edited@example.com");
        check(original.getEmail().equals("alice@example.com"),"editing working copy does not change committed model before Save");
        check(controller.editContact(original,working),"edit controller executes replace command");
        check(controller.getSize()==1 && controller.getContact(0).getId().equals(original.getId()),"edit retains ID without duplicate record");
        reload.loadContacts(context);check(reload.getContact(0).getEmail().equals("edited@example.com"),"edited email persisted");
        Contact bob=new Contact("bob","bob@example.com",null);check(controller.addContact(bob),"second contact saved");
        rejected(()->controller.editContact(working,new Contact("bob","x@y",working.getId())),"username","rename to existing username rejected");
        check(controller.getContactList().getContactByUsername("alice")!=null,"rejected edit retains original");
        String json=new String(Files.readAllBytes(directory.resolve("contacts.sav")),"UTF-8");
        check(!json.contains("observers") && !json.contains("Controller"),"JSON excludes observer/controller references");
        final int[] afterReload={0};reload.addObserver(c->afterReload[0]++);reload.getContact(0).setEmail("notification@example.com");
        check(afterReload[0]==1,"deserialized contacts reconnect to list observer propagation");
        byte[] committed=Files.readAllBytes(directory.resolve("contacts.sav"));
        context.setFailWrites(true);
        check(!controller.addContact(new Contact("carol","c@e",null)),"save failure reported by add controller");
        check(controller.getSize()==2 && controller.getContactByUsername("carol")==null,"failed add rolls back memory");
        check(!controller.editContact(working,new Contact("alice","failed@example.com",working.getId())),"save failure reported by edit controller");
        check(controller.getContactByUsername("alice").getEmail().equals("edited@example.com"),"failed edit restores prior contact");
        check(!controller.deleteContact(bob) && controller.getSize()==2,"failed delete restores removed contact");
        check(Arrays.equals(committed,Files.readAllBytes(directory.resolve("contacts.sav"))),"failed writes preserve committed file");
        context.setFailWrites(false);
        Item item=new Item("Camera","Canon","Digital camera",new Dimensions("12","8","7"),null,null);
        ItemList items=new ItemList();ItemListController itemController=new ItemListController(items,context);
        check(itemController.addItem(item),"item controller saves initial available item");
        check(!controller.isActiveBorrower(working),"available item does not block contact editing");
        item.setStatus("Borrowed");item.setBorrower(new Contact("alice","embedded@example.com",working.getId()));items.saveItems(context);
        check(controller.isActiveBorrower(working),"active borrower detected across separately loaded identity");
        rejected(()->controller.editContact(working,new Contact("alice","blocked@example.com",working.getId())),"contact","active borrower edit blocked");
        rejected(()->controller.deleteContact(working),"contact","active borrower deletion blocked");
        check(controller.getSize()==2,"active borrower refusals preserve directory");
        item.setStatus("Available");item.setBorrower(null);items.saveItems(context);
        check(controller.deleteContact(working),"returned item permits contact deletion");
        reload.loadContacts(context);check(reload.getSize()==1 && reload.getContact(0).getUsername().equals("bob"),"deletion persisted without losing unrelated contact");
        ContactList empty=new ContactList();ContactListController emptyController=new ContactListController(empty,context);
        rejected(()->emptyController.requireBorrowerOptions(),"borrower","empty contact list cannot supply borrower options");
        Item draftItem=new Item("","","",new Dimensions("","",""),null,null);
        ItemController form=new ItemController(draftItem);final int[] itemUpdates={0};draftItem.addObserver(i->itemUpdates[0]++);
        form.updateItem("Camera","Canon","Camera","12","8","7",null,false,bob);
        check(itemUpdates[0]==1 && draftItem.getBorrower()==bob && draftItem.getStatus().equals("Borrowed"),"item form sends coherent observer update with borrower");
        rejected(()->form.updateItem("Camera","Canon","Camera","12","8","7",null,false,null),"borrower","item controller requires borrower for Borrowed");
        rejected(()->form.updateItem("","Canon","Camera","12","8","7",null,true,null),"title","item controller validates required fields");
        final int[] itemListUpdates={0};ItemList observedItems=new ItemList();observedItems.addObserver(i->itemListUpdates[0]++);
        observedItems.addItem(draftItem);draftItem.setTitle("Updated camera");
        check(itemListUpdates[0]==2,"item list observes child model changes");
        check(observedItems.filterItemsByStatus("Borrowed").size()==1 && observedItems.filterItemsByStatus("Available").isEmpty(),"item list status filtering retained");
        System.out.println("RESULT: "+checks+" MVC contract checks passed; production models/controllers/commands, filesystem Context double; no Android UI execution.");
    }
}
