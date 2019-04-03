package ru.volgactf.shop.models;

public class Message {
    private String text;

    public String getText() {
        return this.text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public Message() {
    }

    public Message(String text) {
        this.text = text;
    }

    public String toString() {
        return this.text;
    }
}
