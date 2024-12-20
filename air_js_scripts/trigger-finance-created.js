let config = input.config();

let intExpenses = base.getTable("Internal expanses by group");
let expenses = base.getTable("Finance");
let expense = await expenses.selectRecordAsync(config.expanseId);
let groups = base.getTable("Группы");
let persons = base.getTable("Участники");

if (!expense) {
  return;
}

// Delete all internal expanses§
console.log("Exp: " + expense.getCellValueAsString("Summary"));
let intExp2Del = expense.getCellValue("Internal expanses by group");
if (intExp2Del) {
  console.log("To delete: " + intExp2Del);
  intExpenses.deleteRecordsAsync(intExp2Del.map((rec) => rec.id));
}

// Create new internal expanses
let intExp2Create = [];
if (expense.getCellValue("Тип начисления").name == "По группам") {
  for (let item of expense.getCellValue("Группы")) {
    let group = await groups.selectRecordAsync(item.id);
    if (!group) {
      console.log("Group is not found " + item.id)
      return;
    }

    let percent = group.getCellValue("Количество участников в группе") / expense.getCellValue("Количество всего участников");
    intExp2Create.push({
      fields: {
      "Группа": [{id: group.id}],
      "Трата на группу": expense.getCellValue("Amount (₪)") * percent,
      "Ссылка на трату": [{id:expense.id}]
    }})
  }
}
else {
  if (expense.getCellValue("Тип начисления").name == "По людям") {
    console.log("By people");
    let totalExpense = expense.getCellValue("Amount (₪)");
    let linkedUsers = expense.getCellValue("Люди");
    console.log(linkedUsers);
    if (!linkedUsers || linkedUsers.length === 0) {
        throw new Error("No users linked to the Finance record.");
    }

    // Count users per group
    let groupCounts = {};
    for (let item of linkedUsers) {
        let userRecord = await persons.selectRecordAsync(item.id);
        console.log(userRecord);
        console.log("G");
        if (!userRecord || !userRecord.getCellValue("Группа")) {
          console.log("userRecord is not found " + item.id)
          return;
        }
        console.log(userRecord.getCellValue("Группа"));
        let group = userRecord.getCellValue("Группа")[0]?.id;

        if (group) {
            groupCounts[group] = (groupCounts[group] || 0) + 1;
        }
    }

    console.log("Group counts");
    console.log(groupCounts);

    // Calculate total users linked to this Finance record
    let totalUsers = linkedUsers.length;
    console.log(totalExpense);

    for (let [group, count] of Object.entries(groupCounts)) {
        let local_expense = (count / totalUsers) * totalExpense;
        intExp2Create.push({
            fields: {
                "Группа": [{ id: group }],
                "Трата на группу": local_expense,
                "Ссылка на трату": [{ id: expense.id }]
            }
        });
    }
  }
}

console.log(intExp2Create);
await intExpenses.createRecordsAsync(intExp2Create);
