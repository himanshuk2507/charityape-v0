#!/usr/bin/env bash

###########
# A script which finds any migrations not yet merged to develop, and
# ensures it is timestamped last in the directory and with an updated revision number.

# Similar in effect to `alembic merge heads`, but neater...
###########

# Common
Green='\033[0;32m'
Red='\033[0;31m'
Color_Off='\033[0m'

# eg pretty_print(color, colorised_text, normal_text)
function pretty_print {
    echo -e "$1 $2 $Color_Off $3"
}

cd ..
BASEPATH=new_skraggle
git fetch -a

# Step 1 : Find any migrations not yet in develop
UNMERGED_MIGRATIONS=(`git diff --name-only --diff-filter=A origin/develop | grep migrations/versions`)
if [ -z "$UNMERGED_MIGRATIONS" ]; then
    pretty_print $Red "No unmerged migrations!"
    exit
fi

for i in "${UNMERGED_MIGRATIONS[@]}"
do
   pretty_print $Green "Found unmerged migration: " $i
done

# Step 2 : Find the last migration merged to develop
LAST_MERGED_MIGRATION=`ls -1 $BASEPATH/migrations/versions/*.py |
{
    while read N
        do
        if [[ ! ${UNMERGED_MIGRATIONS[@]} =~ "${N}" ]]; then
            echo $N
        fi
        done

} | tail -n1`

pretty_print $Green "Last merged migration: " $LAST_MERGED_MIGRATION

# Step 3 : Parse the last migration file and find the line which says "revision = 'abc123'"
LAST_REVISION=`cat $LAST_MERGED_MIGRATION | grep "revision = " | head -n1 | sed -n " s,[^']*'\([^']*\).*,\1,p "`
pretty_print $Green "Last revision: " $LAST_REVISION

LAST_MERGED_TIMESTAMP=`echo $LAST_MERGED_MIGRATION | cut -d'/' -f4 | cut -d'_' -f1`
pretty_print $Green "Last merged timestamp: " $LAST_MERGED_TIMESTAMP

# Step 4 : Update the unmerged migrations to link to the last merged
for migration in "${UNMERGED_MIGRATIONS[@]}"
do
    pretty_print $Red "------ Relinking: " $migration

    CURRENT_DOWN_REVISION=`cat $migration | grep "down_revision = " | head -n1 | sed -n " s,[^']*'\([^']*\).*,\1,p "`
    CURRENT_REVISION=`cat $migration | grep "revision = " | head -n1 | sed -n " s,[^']*'\([^']*\).*,\1,p "`
    pretty_print $Red "Modifying unmerged revision: " $CURRENT_DOWN_REVISION
    sed -i'.bak' "s/down_revision = '$CURRENT_DOWN_REVISION'/down_revision = '$LAST_REVISION'/" $migration
    rm "$migration.bak"

    # Step 5 : Move unmerged migrations to last file in directory
    LAST_UNMERGED_TIMESTAMP=`echo $migration | cut -d'/' -f4 | cut -d'_' -f1`
    VERSIONS_DIRECTORY=`echo $migration | cut -d'/' -f3`
    NEW_MIGRATION_TIMESTAMP=`echo $(($LAST_MERGED_TIMESTAMP + 1))`
    NEW_MIGRATION_FILENAME="migrations/${VERSIONS_DIRECTORY}/${NEW_MIGRATION_TIMESTAMP}_.py"
    echo "Will create -----> $NEW_MIGRATION_FILENAME"

    # Store this migrations filename and timestamp so next migration in loop is also updated correctly
    LAST_REVISION=$CURRENT_REVISION
    LAST_MERGED_TIMESTAMP=NEW_MIGRATION_TIMESTAMP

    pretty_print $Red "Renaming file: " $NEW_MIGRATION_TIMESTAMP
    mv $migration "$BASEPATH/$NEW_MIGRATION_FILENAME"
done