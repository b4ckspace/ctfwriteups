package ru.volgactf.shop.models;

import java.io.Serializable;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

@Entity
public class Product implements Serializable {
    @Id
    @GeneratedValue
    private Integer id;
    private String title;
    private String description;
    private Integer price;

    public Product() {
    }

    public Product(String title, String description, Integer price) {
        this.title = title;
        this.description = description;
        this.price = price;
    }

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String toString() {
        return "Product{id=" + this.id + ", title=" + this.title + ", description=" + this.description + ", price=" + this.price + '}';
    }

    public String getTitle() {
        return this.title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Integer getPrice() {
        return this.price;
    }

    public void setPrice(Integer price) {
        this.price = price;
    }
}
