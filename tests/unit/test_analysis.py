from src.analytics.core import TurnAnalysis, analyze_turn, summarize_call


def test_bant_and_summary_are_based_on_explicit_signals():
    turns = [
        analyze_turn("I need inventory help and I am the owner."),
        analyze_turn("My budget is 3000 rupees and I need it this month."),
        analyze_turn("I'm frustrated about the manual work."),
    ]
    result = summarize_call(turns, booked=True)
    assert result.rating == "Hot" and result.score == 100
    assert len(result.reasons) == 4
    assert result.sentiment[-1] == "Negative"
    assert "demo" in result.next_action.lower()
    assert result.follow_up_draft
    assert all(isinstance(turn, TurnAnalysis) for turn in turns)
    cold = summarize_call([analyze_turn("Hi.")], booked=False)
    assert cold.rating == "Cold" and cold.score == 0
