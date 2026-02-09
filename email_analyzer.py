import spacy
import dateparser
from datetime import datetime
import sys

# ----------------------------
# 1. LOAD SPACY MODEL
# ----------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("\n❌ Error: spaCy model 'en_core_web_sm' not found.")
    print("Please run this in terminal: python -m spacy download en_core_web_sm")
    sys.exit()

# ----------------------------
# 2. CONFIG (Keywords & Logic)
# ----------------------------

# Tasks detection keywords
TASK_KEYWORDS = {
    "submit", "send", "reply", "attend", "join",
    "complete", "finish", "upload", "review",
    "call", "meet", "schedule", "email", "prepare"
}

# Urgency detection keywords
URGENT_WORDS = {
    "urgent", "asap", "immediately", "priority",
    "critical", "important", "quick"
}

# ----------------------------
# 3. EXTRACTION FUNCTIONS
# ----------------------------

def extract_dates(text):
    """Extract and normalize dates using spaCy + dateparser"""
    doc = nlp(text)
    found_dates = []

    for ent in doc.ents:
        if ent.label_ == "DATE":
            # Parsing date and looking for future dates
            parsed = dateparser.parse(
                ent.text,
                settings={"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now()}
            )

            if parsed:
                found_dates.append({
                    "original_text": ent.text,
                    "formatted_date": parsed.strftime("%Y-%m-%d"),
                    "dt_obj": parsed
                })
    return found_dates

def extract_tasks(text):
    """Identify tasks using Lemmatization (base form of verbs)"""
    doc = nlp(text)
    tasks = set()

    for token in doc:
        # Check if the root word (lemma) is in our TASK_KEYWORDS
        if token.lemma_.lower() in TASK_KEYWORDS:
            tasks.add(token.lemma_.lower())

    return list(tasks)

# ----------------------------
# 4. PRIORITY SCORING LOGIC
# ----------------------------

def calculate_priority(text, dates, tasks):
    """
    Scoring: 1 (Low) to 10 (High)
    """
    score = 1
    lower_text = text.lower()

    # Bonus for Urgent keywords (+3)
    if any(word in lower_text for word in URGENT_WORDS):
        score += 3

    # Bonus for Tasks found (+2)
    if tasks:
        score += 2

    # Bonus for Deadlines (+1 to +4 based on closeness)
    if dates:
        now = datetime.now()
        proximity_bonus = 0
        for d in dates:
            days_left = (d["dt_obj"] - now).days
            
            if days_left <= 0:      # Today or Overdue
                proximity_bonus = max(proximity_bonus, 4)
            elif days_left <= 1:    # Tomorrow
                proximity_bonus = max(proximity_bonus, 3)
            elif days_left <= 3:    # Within 3 days
                proximity_bonus = max(proximity_bonus, 2)
            else:                   # Far future
                proximity_bonus = max(proximity_bonus, 1)
        score += proximity_bonus

    return min(score, 10) # Max limit 10

# ----------------------------
# 5. MAIN PIPELINE
# ----------------------------

def analyze_email(text):
    dates = extract_dates(text)
    tasks = extract_tasks(text)
    priority = calculate_priority(text, dates, tasks)

    # Clean the output for display
    display_dates = [{"text": d["original_text"], "date": d["formatted_date"]} for d in dates]

    return {
        "email": text.strip(),
        "deadlines": display_dates,
        "tasks": tasks,
        "priority": priority
    }

# ----------------------------
# 6. RUN THE TEST
# ----------------------------

if __name__ == "__main__":
    # Sample Input
    sample_email = """
    Hi team, please submit the project report by Friday. 
    Also, attend the client meeting on 10 Feb. 
    This is urgent, so reply ASAP.
    """

    result = analyze_email(sample_email)

    # Output Formatting
    print("\n" + "="*40)
    print("       📧 EMAIL SMART ANALYSIS")
    print("="*40)

    print(f"\n[TEXT]: {result['email']}")
    
    print("\n[DEADLINES FOUND]:")
    if result['deadlines']:
        for d in result['deadlines']:
            print(f"  📅 {d['text']} -> {d['date']}")
    else:
        print("  None detected.")

    print(f"\n[TASKS DETECTED]: {', '.join(result['tasks']) if result['tasks'] else 'None'}")

    print(f"\n[PRIORITY SCORE]: {result['priority']}/10")
    
    if result['priority'] >= 7:
        status = "🔴 HIGH (Action Required Now)"
    elif result['priority'] >= 4:
        status = "🟡 MEDIUM (Plan for this week)"
    else:
        status = "🟢 LOW (Routine task)"
    
    print(f"[STATUS]: {status}")
    print("\n" + "="*40)