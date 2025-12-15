"""
MCP Server for Educational Facts
Provides a Model Context Protocol server that returns educational facts
about various topics to ground stories in reality.
"""

from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Educational Facts Server")

# Hardcoded educational facts database
EDUCATIONAL_FACTS = {
    "space": {
        "mars": "Mars is the fourth planet from the Sun and is known as the Red Planet due to iron oxide on its surface. A day on Mars is about 24.6 hours, similar to Earth. Mars has two small moons: Phobos and Deimos.",
        "moon": "The Moon is Earth's only natural satellite. It takes about 27.3 days to orbit Earth. The Moon's gravity causes ocean tides on Earth. Humans first landed on the Moon in 1969.",
        "sun": "The Sun is a star at the center of our solar system. It's about 4.6 billion years old and provides light and heat to all planets. The Sun is so large that about 1.3 million Earths could fit inside it.",
        "stars": "Stars are giant balls of hot gas that produce light and heat through nuclear fusion. The closest star to Earth is the Sun. Stars come in different colors: blue (hottest), white, yellow, orange, and red (coolest).",
        "planets": "There are 8 planets in our solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. The first four are rocky planets, and the last four are gas giants."
    },
    "dinosaurs": {
        "t-rex": "Tyrannosaurus Rex, or T-Rex, lived about 68-66 million years ago. It was one of the largest meat-eating dinosaurs, about 40 feet long and 12 feet tall. T-Rex had powerful jaws with teeth up to 8 inches long.",
        "triceratops": "Triceratops was a plant-eating dinosaur with three horns on its head. It lived about 68-66 million years ago and was about 30 feet long. The name Triceratops means 'three-horned face'.",
        "brachiosaurus": "Brachiosaurus was one of the tallest dinosaurs, with a very long neck. It was a plant-eater that lived about 154-153 million years ago. It could reach heights of up to 50 feet tall.",
        "stegosaurus": "Stegosaurus was a plant-eating dinosaur with distinctive plates along its back and spikes on its tail. It lived about 155-150 million years ago and was about 30 feet long."
    },
    "animals": {
        "elephants": "Elephants are the largest land animals on Earth. They have excellent memories and can live up to 70 years. African elephants have larger ears than Asian elephants. Elephants use their trunks to breathe, smell, touch, and grab things.",
        "whales": "Whales are the largest animals in the ocean. Blue whales are the biggest animals that have ever lived on Earth, even bigger than dinosaurs. Whales are mammals, which means they breathe air and feed milk to their babies.",
        "penguins": "Penguins are birds that cannot fly but are excellent swimmers. They live in cold places like Antarctica. Penguins have waterproof feathers and can dive deep into the ocean to catch fish. They walk upright and often slide on their bellies.",
        "lions": "Lions are known as the 'king of the jungle' and live in groups called prides. Male lions have manes around their heads. Lions are carnivores and hunt in groups. They can sleep up to 20 hours a day.",
        "dolphins": "Dolphins are highly intelligent marine mammals. They communicate using clicks and whistles. Dolphins are known for their playful behavior and can jump high out of the water. They live in groups called pods."
    },
    "ocean": {
        "coral": "Coral reefs are underwater structures made by tiny animals called coral polyps. They are home to many colorful fish and sea creatures. Coral reefs are often called the 'rainforests of the sea' because of their biodiversity.",
        "sharks": "Sharks have been around for over 400 million years. They have special sensors that can detect electrical fields from other animals. Most sharks are not dangerous to humans. Sharks have no bones - their skeletons are made of cartilage.",
        "octopus": "Octopuses are very intelligent sea creatures with 8 arms. They can change color and texture to blend in with their surroundings. Octopuses have three hearts and blue blood. They can squeeze through very small spaces."
    }
}


def _get_educational_fact_impl(topic: str) -> str:
    """
    Core implementation for retrieving educational facts.
    This function can be tested directly without MCP decorator.
    
    Args:
        topic: The topic to get a fact about (e.g., "Mars", "T-Rex", "Elephants")
    
    Returns:
        A string containing an educational fact about the topic, or a message
        if the topic is not found in the knowledge base.
    """
    topic_lower = topic.lower().strip()
    
    # Search through all categories
    for category, facts in EDUCATIONAL_FACTS.items():
        if topic_lower in facts:
            return facts[topic_lower]
        
        # Also check if topic matches category keywords
        if topic_lower in category or any(keyword in topic_lower for keyword in category.split()):
            # Return a general fact from that category
            first_key = next(iter(facts))
            return f"Here's a fact about {topic}: {facts[first_key]}"
    
    # If not found, return a helpful message
    available_topics = []
    for category, facts in EDUCATIONAL_FACTS.items():
        available_topics.extend(facts.keys())
    
    return f"I don't have specific facts about '{topic}' yet. Available topics include: {', '.join(available_topics[:10])}. I'll use general knowledge to make the story educational!"


@mcp.tool()
def get_educational_fact(topic: str) -> str:
    """
    Retrieves an educational fact about a given topic.
    This tool helps ground stories in real-world facts to make them educational.
    
    Args:
        topic: The topic to get a fact about (e.g., "Mars", "T-Rex", "Elephants")
    
    Returns:
        A string containing an educational fact about the topic, or a message
        if the topic is not found in the knowledge base.
    """
    return _get_educational_fact_impl(topic)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

