load('helpers/runMigration.js');

function migrate() {
  const result = db.cats.createIndex({"name": 1}, {unique: true});

  if (result.ok !== 1) {
    throw new Error(tojson(result));
  }
}

runMigration(migrate, 2);
