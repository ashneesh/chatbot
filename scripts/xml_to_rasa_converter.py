#!/usr/bin/env python3
"""
XML to Rasa Converter
Converts healthcare XML datasets to Rasa training format
"""

import xml.etree.ElementTree as ET
import yaml
import argparse
import os
from typing import Dict, List, Any
import re

class XMLToRasaConverter:
    def __init__(self):
        self.intents = {}
        self.entities = {}
        self.responses = {}
        self.stories = []

    def convert_xml_file(self, xml_file: str, output_dir: str):
        """Convert XML file to Rasa format"""
        print(f"Converting {xml_file} to Rasa format...")

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Parse based on XML structure
            if root.tag == "conversations":
                self._parse_conversations(root)
            elif root.tag == "qa_pairs":
                self._parse_qa_pairs(root)
            else:
                print(f"Unsupported XML format: {root.tag}")
                return

            # Generate Rasa files
            self._generate_nlu_file(output_dir)
            self._generate_domain_file(output_dir)
            self._generate_stories_file(output_dir)

            print("✅ Conversion completed successfully!")

        except Exception as e:
            print(f"❌ Error converting XML: {e}")

    def _parse_conversations(self, root):
        """Parse conversation format XML"""
        for conv in root.findall("conversation"):
            for turn in conv.findall("turn"):
                user_text = turn.find("user")
                bot_text = turn.find("bot")

                if user_text is not None and bot_text is not None:
                    intent = self._extract_intent(user_text.text)
                    self._add_training_example(intent, user_text.text)
                    self._add_response(intent, bot_text.text)

    def _parse_qa_pairs(self, root):
        """Parse Q&A format XML"""
        for item in root.findall("item"):
            question = item.find("question")
            answer = item.find("answer")

            if question is not None and answer is not None:
                intent = self._extract_intent(question.text)
                self._add_training_example(intent, question.text)
                self._add_response(intent, answer.text)

    def _extract_intent(self, text: str) -> str:
        """Extract intent from text using keywords"""
        text_lower = text.lower()

        # Healthcare intent mapping
        intent_keywords = {
            "report_symptom": ["symptom", "pain", "hurt", "feel", "sick", "ache"],
            "book_appointment": ["appointment", "schedule", "book", "visit", "see doctor"],
            "emergency": ["emergency", "urgent", "911", "help", "severe"],
            "get_advice": ["advice", "recommend", "should", "what to do"],
            "goodbye": ["bye", "goodbye", "thank", "thanks"],
            "greet": ["hello", "hi", "hey", "good morning"]
        }

        for intent, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent

        return "general_inquiry"

    def _add_training_example(self, intent: str, text: str):
        """Add training example for intent"""
        if intent not in self.intents:
            self.intents[intent] = []

        # Simple entity extraction
        entities = self._extract_entities(text)
        if entities:
            # Format with entities
            formatted_text = self._format_entities(text, entities)
            self.intents[intent].append(formatted_text)
        else:
            self.intents[intent].append(text)

    def _extract_entities(self, text: str) -> List[Dict]:
        """Simple entity extraction"""
        entities = []

        # Healthcare entities
        symptom_patterns = ["headache", "fever", "cough", "pain", "nausea"]
        body_part_patterns = ["head", "chest", "stomach", "back", "throat"]

        for pattern in symptom_patterns:
            if pattern in text.lower():
                start = text.lower().find(pattern)
                entities.append({
                    "entity": "symptom",
                    "value": pattern,
                    "start": start,
                    "end": start + len(pattern)
                })

        for pattern in body_part_patterns:
            if pattern in text.lower():
                start = text.lower().find(pattern)
                entities.append({
                    "entity": "body_part", 
                    "value": pattern,
                    "start": start,
                    "end": start + len(pattern)
                })

        return entities

    def _format_entities(self, text: str, entities: List[Dict]) -> str:
        """Format text with entity annotations"""
        formatted = text
        for entity in sorted(entities, key=lambda x: x["start"], reverse=True):
            start, end = entity["start"], entity["end"]
            value = entity["value"]
            entity_type = entity["entity"]
            formatted = formatted[:start] + f"[{value}]({entity_type})" + formatted[end:]
        return formatted

    def _add_response(self, intent: str, text: str):
        """Add response for intent"""
        response_key = f"utter_{intent}"
        if response_key not in self.responses:
            self.responses[response_key] = []

        self.responses[response_key].append({"text": text})

    def _generate_nlu_file(self, output_dir: str):
        """Generate NLU training file"""
        nlu_data = {
            "version": "3.1",
            "nlu": []
        }

        for intent, examples in self.intents.items():
            nlu_data["nlu"].append({
                "intent": intent,
                "examples": "\n".join([f"- {example}" for example in examples])
            })

        with open(os.path.join(output_dir, "nlu.yml"), "w") as f:
            yaml.dump(nlu_data, f, default_flow_style=False)

        print(f"✅ Generated NLU file with {len(self.intents)} intents")

    def _generate_domain_file(self, output_dir: str):
        """Generate domain file"""
        domain_data = {
            "version": "3.1",
            "intents": list(self.intents.keys()),
            "responses": self.responses,
            "actions": [f"action_{intent}" for intent in self.intents.keys()],
            "session_config": {
                "session_expiration_time": 60,
                "carry_over_slots_to_new_session": True
            }
        }

        with open(os.path.join(output_dir, "domain.yml"), "w") as f:
            yaml.dump(domain_data, f, default_flow_style=False)

        print(f"✅ Generated domain file")

    def _generate_stories_file(self, output_dir: str):
        """Generate simple stories file"""
        stories_data = {
            "version": "3.1", 
            "stories": []
        }

        # Generate basic stories
        for intent in self.intents.keys():
            story = {
                "story": f"{intent} path",
                "steps": [
                    {"intent": intent},
                    {"action": f"utter_{intent}"}
                ]
            }
            stories_data["stories"].append(story)

        with open(os.path.join(output_dir, "stories.yml"), "w") as f:
            yaml.dump(stories_data, f, default_flow_style=False)

        print(f"✅ Generated stories file with {len(self.intents)} stories")

def main():
    parser = argparse.ArgumentParser(description="Convert XML healthcare datasets to Rasa format")
    parser.add_argument("xml_file", help="Input XML file path")
    parser.add_argument("-o", "--output", default="../rasa/data", help="Output directory")

    args = parser.parse_args()

    if not os.path.exists(args.xml_file):
        print(f"❌ XML file not found: {args.xml_file}")
        return

    os.makedirs(args.output, exist_ok=True)

    converter = XMLToRasaConverter()
    converter.convert_xml_file(args.xml_file, args.output)

if __name__ == "__main__":
    main()
