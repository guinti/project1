from bot_info_file import bot, conn
from targets_functions import send_purposes


@bot.callback_query_handler(func=lambda call: call.data.startswith('purp_done'))
def purpose_done(call):
    sub_number = call.data[9:]
    cur = conn.cursor()
    cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?", (call.from_user.id, int(sub_number)))
    row = cur.fetchone()
    if len(sub_number) == 1:
        if row[4] < 100:
            cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                        (100, call.from_user.id, int(sub_number)))
            conn.commit()
        else:
            cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?", (call.from_user.id, int(sub_number)))
            rows = cur.fetchall()
            sum = 0
            t = 0
            for purp in rows:
                sum += purp[4] * purp[5] // 100
                if purp[4] != 100:
                    t = 1
            if t == 0:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (100, call.from_user.id, int(sub_number)))
            else:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (sum, call.from_user.id, int(sub_number)))
            conn.commit()

    if len(sub_number) == 2:
        if row[4] < 100:
            cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                        (100, call.from_user.id, int(sub_number)))
            conn.commit()
        else:
            cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?", (call.from_user.id, int(sub_number)))
            rows = cur.fetchall()
            sum_new = 0
            for purp in rows:
                sum_new += purp[4] * purp[5] // 100
            if sum_new >= 96:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (100, call.from_user.id, int(sub_number)))
            else:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (sum_new, call.from_user.id, int(sub_number)))
            conn.commit()
        cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?", (call.from_user.id, int(sub_number) // 10))
        rows = cur.fetchall()
        cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?",
                    (call.from_user.id, int(sub_number) // 10))
        purpose_1 = cur.fetchone()[4]
        if row[4] == 100 or (purpose_1 != 100 and row[4] < 100):
            summ = 0
            t = 0
            for purpose in rows:
                summ += purpose[4] * purpose[5] // 100
                if purpose[4] != 100:
                    t = 1
            if t == 0:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (100, call.from_user.id, int(sub_number) // 10))
            else:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (summ, call.from_user.id, int(sub_number) // 10))
            conn.commit()

    if len(sub_number) == 3:
        if row[4] < 100:
            cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                        (100, call.from_user.id, int(sub_number)))
            conn.commit()
        else:
            cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                        (0, call.from_user.id, int(sub_number)))
            conn.commit()

        cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?", (call.from_user.id, int(sub_number) // 10))
        rows = cur.fetchall()
        cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?",
                    (call.from_user.id, int(sub_number) // 10))
        purpose_1 = cur.fetchone()[4]
        if row[4] == 100 or (purpose_1 != 100 and row[4] < 100):
            summ = 0
            for purpose in rows:
                summ += purpose[4] * purpose[5] // 100
            if summ >= 96:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (100, call.from_user.id, int(sub_number) // 10))
            else:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (summ, call.from_user.id, int(sub_number) // 10))
            conn.commit()
        cur.execute("SELECT * FROM purposes WHERE id=? AND purpose_above=?",
                    (call.from_user.id, int(sub_number) // 100))
        rows = cur.fetchall()
        cur.execute("SELECT * FROM purposes WHERE id=? AND subgoal_number=?",
                    (call.from_user.id, int(sub_number) // 100))
        purpose_1 = cur.fetchone()
        if row[4] == 100 or (purpose_1[4] != 100 and row[4] < 100):
            summ = 0
            t = 0
            for purpose in rows:
                summ += purpose[4] * purpose[5] // 100
                if purpose[4] != 100:
                    t = 1
            if t == 0:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (100, call.from_user.id, int(sub_number) // 100))
            else:
                cur.execute("UPDATE purposes SET done_percentage=? WHERE id=? AND subgoal_number=?",
                            (summ, call.from_user.id, int(sub_number) // 100))
            conn.commit()
    send_purposes(sub_number, call)
