package ru.volgactf.shop.dao;

import java.util.List;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.criteria.CriteriaBuilder;
import javax.persistence.criteria.CriteriaQuery;
import javax.persistence.criteria.Predicate;
import javax.persistence.criteria.Root;
import javax.transaction.Transactional;
import org.hibernate.Hibernate;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Repository;
import ru.volgactf.shop.models.User;

@Transactional
@Repository
public class UserDao {
    @PersistenceContext
    protected EntityManager entityManager;

    public UserDao() {
    }

    public User register(String name, String pass) {
        User user = new User(name, pass, 100);
        this.entityManager.persist(user);
        return user;
    }

    public User login(String name, String pass) {
        CriteriaBuilder cb = this.entityManager.getCriteriaBuilder();
        CriteriaQuery<User> q = cb.createQuery(User.class);
        Root<User> c = q.from(User.class);
        q.select(c);
        q.where(new Predicate[]{cb.equal(c.get("name"), name), cb.equal(c.get("pass"), pass)});
        List<User> users = this.entityManager.createQuery(q).getResultList();
        return users.isEmpty() ? null : (User)users.get(0);
    }

    public void update(User user) {
        this.entityManager.merge(user);
    }

    public void save(User user) {
        this.entityManager.persist(user);
    }

    public User findByName(String name) throws DataAccessException {
        CriteriaBuilder cb = this.entityManager.getCriteriaBuilder();
        CriteriaQuery<User> q = cb.createQuery(User.class);
        Root<User> c = q.from(User.class);
        q.select(c);
        q.where(cb.equal(c.get("name"), name));
        List<User> users = this.entityManager.createQuery(q).getResultList();
        return users.isEmpty() ? null : (User)users.get(0);
    }

    public User getUser(Integer id) throws DataAccessException {
        User user = (User)this.entityManager.find(User.class, id);
        if (user != null) {
            Hibernate.initialize(user.getCartItems());
        }

        return user;
    }
}
