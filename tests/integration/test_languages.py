from fastapi.testclient import TestClient

from src.api.app import create_app


def test_english_hindi_hinglish_switch_in_one_call(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MODE", "mock")
    monkeypatch.setenv("CRM_PATH", str(tmp_path / "languages.sqlite3"))
    with TestClient(create_app()).websocket_connect("/ws/text") as socket:
        socket.receive_json()

        def ask(text):
            socket.send_json({"text": text})
            while (reply := socket.receive_json())["type"] != "reply":
                pass
            return reply, socket.receive_json()

        for detail, yes, spoken, count, date in (
            ("Three stores on 4 December 2026", "Yes", "3 stores", 3, "2026-12-04"),
            ("चार दुकानें ५ दिसंबर २०२६", "हाँ", "4 दुकानें", 4, "2026-12-05"),
            ("paanch dukaan 6 December 2026", "haan", "5 stores", 5, "2026-12-06"),
        ):
            reply, profile = ask(detail)
            assert spoken in reply["text"]
            assert profile["pending"] == {"store_count": count, "target_date": date}
            _, profile = ask(yes)
            assert profile["profile"]["store_count"] == count
            assert profile["profile"]["target_date"] == date

        for query in ("What does Growth cost?", "ग्रोथ की कीमत क्या है?", "Growth ka price kya hai?"):
            reply, _ = ask(query)
            assert reply["citation"]["id"] == "growth" and "2,499" in reply["text"]
        for contact in (
            "My phone is +91 98765 43210",
            "मेरा फोन +९१ ९८७६५ ४३२१०",
            "mera phone +91 98765 43210",
        ):
            reply, _ = ask(contact)
            assert reply["mode"] == "booking"
        reply, _ = ask("kal")
        assert reply["mode"] != "session"
