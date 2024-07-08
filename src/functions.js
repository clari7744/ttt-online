function createElement(name, options) {
    let element = document.createElement(name);
    for (let [k, v] of Object.entries(options)) element.setAttribute(k, v);
    return element;
}
async function setSpace(elem, name) {
    let args = `game=${
        document.getElementById("game_id").content
    }&space=${elem}`;
    if (name) args += `&user=${name}`;
    let resp = await fetch(`${document.location.origin}/setSpace?${args}`);
    let s = resp.status;
    resp = await resp.json();
    if (s != 200) {
        return alert(resp.message);
    }
    document.getElementById(elem).innerHTML = resp.move;
}
async function joinGame(gid, name, aiGame = false) {
    resp = await fetch(
        `${document.location.origin}/addPlayer?game=${gid}&user=${name}&ai=${aiGame}`
    );
    s = resp.status;
    resp = await resp.json();
    if (s != 200) {
        return alert(resp.message);
    }
    location.href = `${document.location.origin}/game?game=${gid}&user=${name}`;
}
async function runGame(gid, name) {
    let resp = await fetch(
        `${document.location.origin}/getGame?game=${gid}`
    ).then(r => r.json());
    document.getElementById("div_name").innerHTML = `Username: ${name}`;
    document.getElementById(
        "div_opponent"
    ).innerHTML = `Opponent: Waiting for opponent...`;
    document.getElementById("player_name").content = name;
    document.querySelector("body").appendChild(
        createElement("input", {
            type: "button",
            value: "Share",
            id: "share_button",
            onclick: `share('${gid}');`,
        })
    );
    let on = document.getElementById("opponent_name");
    let ind = resp.players.indexOf(name);
    let nameChanged;
    while (!resp.ended && !nameChanged) {
        resp = await fetch(
            `${document.location.origin}/getGame?game=${gid}`
        ).then(r => r.json());
        document.getElementById(
            "room_name"
        ).innerHTML = `Room Name: ${resp.name}`;
        if (resp.players[ind] != name) nameChanged = false;
        await buildBoard(gid);
        document.getElementById("turn_number").innerHTML = `Turn: Player ${
            resp.turn + 1 || 1
        }${resp.turn == ind ? " (You)" : ""}`;
        await new Promise(r => setTimeout(r, 1000));
        if (resp.ai_game && resp.turn == 1 && !resp.ended) {
            let available = [];
            for (let [r, vals] of Object.entries(resp.board))
                for (let [c, val] of Object.entries(vals))
                    if (val == "") available.push(`${r}${parseInt(c) + 1}`);
            await setSpace(
                available[Math.floor(Math.random() * available.length)],
                "AI"
            );
        }
        if (
            resp.players.every(e => e) &&
            !on.content &&
            (resp.players.length > 1 || resp.ai_game)
        ) {
            on.content = resp.players.filter(p => p != name)[0] || "AI";
            let pl = n =>
                `${n} (Player ${resp.players.indexOf(n) + 1} - ${
                    "XO"[resp.players.indexOf(n)]
                })`;
            document.getElementById("div_name").innerHTML = `Username: ${pl(
                name
            )}`;
            document.getElementById("div_opponent").innerHTML = `Opponent: ${pl(
                on.content
            )}`;
            document.getElementById("share_button").remove();
        }
    }
    if (!nameChanged)
        alert(
            "Game ended!\n" +
                (resp.tie
                    ? "Tie game!"
                    : resp.players[Number(!resp.turn)] + " wins!")
        );
}
async function buildBoard(game) {
    let resp = await fetch(`${document.location.origin}/getBoard?game=${game}`);
    s = resp.status;
    resp = await resp.json();
    if (s != 200) {
        return alert(resp.message);
    }
    let board = document.getElementById("board_div");
    board.innerHTML = "";
    let table = createElement("table", { id: "board_table" });
    for (let r of "abc") {
        let row = createElement("tr", { id: `row_${r}` });
        for (let [i, c] of Object.entries("123")) {
            let col = createElement("td", { id: `${r}${c}` });
            if (!resp[r][i])
                col.appendChild(
                    createElement("input", {
                        type: "button",
                        id: `${r}${c}b`,
                        value: " ",
                        onclick: `setSpace("${r}${c}", document.getElementById('player_name').content)`,
                        class: "ttt_space",
                    })
                );
            else {
                col.innerHTML = resp[r][i];
            }
            row.appendChild(col);
            table.appendChild(row);
        }
    }
    board.appendChild(table);
}
async function changeName(game, user) {
    let newName = prompt("Enter new username:");
    if (!newName) return;
    let resp = await fetch(
        `${document.location.origin}/changeName?game=${game}&user=${user}&name=${newName}`
    );
    s = resp.status;
    resp = await resp.json();
    if (s != 200) {
        return alert(resp.message);
    }
    alert(`Name changed to ${newName}`);
    location.href = `${document.location.origin}/game?game=${game}&user=${newName}`;
}
async function changeRoomName(game) {
    let newName = prompt("Enter new room name:");
    if (!newName) return;
    let resp = await fetch(
        `${document.location.origin}/changeRoomName?game=${game}&name=${newName}`
    );
    s = resp.status;
    resp = await resp.json();
    if (s != 200) {
        return alert(resp.message);
    }
    alert(`Room name changed to ${newName}`);
}

function share(game) {
    let url = `${document.location.origin}/joinGame?game=${game}`;
    const elem = document.createElement("textarea");
    elem.value = `Play TicTacToe with ${
        document.getElementById("player_name").content
    }! Join at ${url}`;
    document.body.appendChild(elem);
    elem.select();
    elem.setSelectionRange(0, 99999);
    document.execCommand("copy");
    document.body.removeChild(elem);
    alert("Copied link to clipboard");
}
