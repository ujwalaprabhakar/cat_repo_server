load('helpers/runMigration.js');

function migrate() {
  let result = db.createCollection("migrations", {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: [ "version", "ctime" ],
        properties: {
          version: {
            bsonType: "int",
            minimum: 1
          },
          ctime: {
            bsonType: "date"
          }
        }
      }
    }
  });

  if (result.ok !== 1) {
    throw new Error(tojson(result));
  }

  result = db.migrations.createIndex({"version": 1}, {unique: true});

  if (result.ok !== 1) {
    throw new Error(tojson(result));
  }
}

runMigration(migrate, 1);
