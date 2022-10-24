# Youtube query command.

desc = 'Queries a random YouTube link'

def execute(data, argv):
    # choose a random youtube link 

    while True:
        c = data.db.conn.cursor()
        c.execute('SELECT * FROM links ORDER BY random() LIMIT 1')

        row = c.fetchone()

        if row is None:
            data.reply('No links!')
            break
        else:
            if 'youtube.com' in row[1]:
                data.bcast(f'A gift from <a href="{row[1]}">{row[0]}</a>')
                break
            else:
                continue
