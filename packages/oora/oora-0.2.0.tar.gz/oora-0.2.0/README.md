# Oora

This is intended as a very thin layer above the sqlite3 package by adding a few QOL features:

- default SQLite PRAGMAs fit for server use
- helpers for common write operations (insert, update)
- very basic (forward only) migrations management
- very basic ORM-like functionality for dataclasses (row <-> dataclass)
- lazy connect

Oora is "sql first" and these are out of scope:

- any kind of automatic schema generation
- query abstraction, query generator


## install

    pip install oora

## Usage

    import oora
    from dataclasses import dataclass

    db = oora.DB(
        db_path=":memory:",  # or /path/to/your/db.sqlite3
        # migrations are just pairs key=>val where key is an arbitrary (but unique) label and val is a SQL script.
        # migrations are executed in order
        migrations={
            # here's an initial migration:
            "0000": "CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);",
            # simulating a schema evolution, let's add a field:
            "0001": "ALTER TABLE user ADD COLUMN email TEXT NULL;",
        },
    )
    db.migrate()

    db.insert("user", {"name": "John"})
    db.insert("user", {"name": "Jack"})
    db.insert("user", {"name": "Jill"})


    # dataclasses are perfect to represent rows
    # while still allowing custom behaviour
    @dataclass
    class User:
        id: int
        name: str
        email: str

        def __str__(self):
            return self.name


    # fetch a random instance
    user = db.hydrate(User, db.execute("select * from user ORDER BY RANDOM() limit 1").fetchone())
    print(f"User(id {user.id}), original name: {user}")

    # change name and email
    user.name = "Richard"
    user.email = "richard@acme.tld"
    db.save(user) # name of table is infered from the dataclass name
    print(f"User(id {user.id}), updated name: {user} <{user.email}>")

    # persist changes
    db.commit()