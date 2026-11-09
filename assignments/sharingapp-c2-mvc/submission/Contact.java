package com.example.sharingapp;

import java.util.ArrayList;
import java.util.UUID;

/** Domain model. Observers receive changes without depending on Android views. */
public class Contact {
    public interface Observer { void onContactChanged(Contact contact); }
    private String username;
    private String email;
    private String id;
    private transient ArrayList<Observer> observers;

    public Contact(String username, String email, String id) {
        this.username = username;
        this.email = email;
        this.id = id == null ? UUID.randomUUID().toString() : id;
    }
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    public String getId() { return id; }
    public void setUsername(String value) {
        if (!same(username, value)) { username = value; notifyObservers(); }
    }
    public void setEmail(String value) {
        if (!same(email, value)) { email = value; notifyObservers(); }
    }
    public void setId() { updateId(UUID.randomUUID().toString()); }
    public void updateId(String value) {
        if (!same(id, value)) { id = value; notifyObservers(); }
    }
    /** Publish one coherent update rather than two partially updated field values. */
    public void update(String username, String email) {
        if (!same(this.username, username) || !same(this.email, email)) {
            this.username = username;
            this.email = email;
            notifyObservers();
        }
    }
    private boolean same(String a, String b) { return a == null ? b == null : a.equals(b); }
    public void addObserver(Observer observer) {
        if (observers == null) { observers = new ArrayList<Observer>(); }
        if (observer != null && !observers.contains(observer)) { observers.add(observer); }
    }
    public void removeObserver(Observer observer) {
        if (observers != null) { observers.remove(observer); }
    }
    public void notifyObservers() {
        if (observers != null) {
            for (Observer observer : new ArrayList<Observer>(observers)) {
                observer.onContactChanged(this);
            }
        }
    }
}
