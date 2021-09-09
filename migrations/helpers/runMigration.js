// NOTE: keep this in a separate helpers/ folder to avoid it to be picked by the migration.sh
// script!

/**
 * Run a migration function and keeps a record of it
 * Ensures that the migration has not already been run (idempotence),
 * preventing to run it twice by accident and potentially breaking the DB.
 */
function runMigration(migration, rawVersion) {
  const version = NumberInt(rawVersion);
  const alreadyRan = db.migrations.findOne({ version }, { _id: 0 });

  if (alreadyRan) {
    const message = `Already ran migration #${JSON.stringify(alreadyRan)}, skipping`;
    print(message);
    return;
  }

  migration();

  db.migrations.insertOne({ version, 'ctime': new Date() });
  print(`Successfully ran migration ${rawVersion}`);
}

function getEnv(name, default_value) {
  let exit_code = run("sh", "-c", `printenv --null ${name} >/tmp/${name}.txt`);
  if (exit_code != 0) {
    return default_value;
  }

  return cat(`/tmp/${name}.txt`)
}

function createIndexes(collection, indexList, extraOptions = {}) {
  indexList.forEach(newIndex => {
    const indexResult = collection.createIndex(newIndex, extraOptions);

    if (indexResult.ok !== 1) {
      throw new Error(tojson(indexResult));
    }
  });
}

function dropIndexes(collection, indexList, extraOptions = {}) {
  indexList.forEach(newIndex => {
    const indexResult = collection.dropIndex(newIndex, extraOptions);

    if (indexResult.ok !== 1) {
      throw new Error(tojson(indexResult));
    }
  });
}
