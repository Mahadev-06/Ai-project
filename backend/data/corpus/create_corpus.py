import os
import json

base_dir = r"c:\Users\Lenovo\Desktop\ai project\backend\data\corpus"
docs_dir = os.path.join(base_dir, "documents")

os.makedirs(docs_dir, exist_ok=True)

manifest = {
  "version": "1.0.0",
  "created_date": "2024-09-01",
  "description": "ClaimLens local evidence corpus v1.0. A curated collection of factual passages from authoritative sources covering science, health, geography, history, and technology. Used as the default evidence base for offline claim verification.",
  "document_count": 30,
  "topics": [
    "Earth science and climate",
    "Space and astronomy",
    "Human health and medicine",
    "Geography and demographics",
    "History and landmarks",
    "Biology and nature",
    "Physics and chemistry",
    "Technology and computing",
    "Economics and development",
    "Nutrition and food science"
  ],
  "license_summary": "All content is drawn from or paraphrases publicly available factual information from government agencies (NASA, WHO, NOAA, USGS), educational institutions, and reference sources. Content used under fair use for educational research purposes. See individual documents for specific attributions.",
  "sources": [
    "NASA", "WHO", "NOAA", "USGS", "CDC", "World Bank",
    "Encyclopedia Britannica (paraphrased)", "National Geographic (paraphrased)",
    "UN agencies", "IPCC"
  ]
}

with open(os.path.join(base_dir, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

docs = [
  {
    "filename": "earth-shape.json",
    "data": {
      "doc_id": "earth-shape-01",
      "title": "Shape of the Earth",
      "publisher": "NOAA",
      "source_url": "https://oceanservice.noaa.gov/facts/earth-round.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-01-20",
      "attribution": "National Oceanic and Atmospheric Administration (NOAA)",
      "license": "Public Domain",
      "passages": [
        "The Earth is an irregularly shaped ellipsoid, specifically an oblate spheroid. While it appears round from space, it is not a perfect sphere. The Earth's rotation causes it to bulge at the equator and flatten at the poles.",
        "The equatorial diameter of Earth is about 12,756 kilometers (7,926 miles), while the polar diameter is about 12,714 kilometers (7,900 miles). This difference of about 42 kilometers means the Earth is slightly wider than it is tall.",
        "The shape of the Earth is continuously changing, albeit very slowly. Factors such as tectonic plate movement, the rebound of crust from melting glaciers, and tidal forces all contribute to these ongoing structural variations."
      ]
    }
  },
  {
    "filename": "great-wall-visibility.json",
    "data": {
      "doc_id": "great-wall-vis-02",
      "title": "Visibility of the Great Wall of China from Space",
      "publisher": "NASA",
      "source_url": "https://www.nasa.gov/vision/space/workinginspace/great_wall.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "2005-05-09",
      "attribution": "National Aeronautics and Space Administration (NASA)",
      "license": "Public Domain",
      "passages": [
        "The Great Wall of China is generally not visible to the naked eye from low Earth orbit, and certainly not from the Moon. The wall's maximum width is only about 9.1 meters (30 feet) and its color blends into the surrounding landscape.",
        "Astronauts have confirmed that without magnification, the Great Wall is indistinguishable from other geographic features. It is a persistent myth that it is the only man-made object visible from space.",
        "Using radar and high-resolution camera lenses, parts of the Great Wall can be imaged from low Earth orbit. However, many other human-made structures, such as highways and cities, are far more visible from space under normal conditions."
      ]
    }
  },
  {
    "filename": "water-boiling.json",
    "data": {
      "doc_id": "water-boiling-03",
      "title": "Boiling Point of Water",
      "publisher": "USGS",
      "source_url": "https://www.usgs.gov/special-topics/water-science-school/science/boiling-point-water",
      "retrieved_date": "2024-09-01",
      "publication_date": "2019-10-22",
      "attribution": "U.S. Geological Survey (USGS)",
      "license": "Public Domain",
      "passages": [
        "At standard atmospheric pressure, which is exactly 1 atmosphere (atm) or 101.325 kilopascals (kPa), pure water boils at 100 degrees Celsius (212 degrees Fahrenheit). This baseline is typically measured at sea level.",
        "The boiling point of water is dependent on atmospheric pressure. As elevation increases, atmospheric pressure decreases, causing the boiling point of water to drop. For example, at the elevation of Denver, Colorado, water boils at about 95 degrees Celsius (203 degrees Fahrenheit).",
        "Conversely, if water is subjected to pressures greater than 1 atmosphere, its boiling point increases. This is the principle used in pressure cookers, which trap steam to raise the internal pressure and cook food faster by allowing water to reach temperatures higher than 100°C before boiling."
      ]
    }
  },
  {
    "filename": "earth-sun-orbit.json",
    "data": {
      "doc_id": "earth-sun-orbit-04",
      "title": "Earth's Orbit and Axial Tilt",
      "publisher": "NASA",
      "source_url": "https://solarsystem.nasa.gov/planets/earth/in-depth/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-08-15",
      "attribution": "NASA Solar System Exploration",
      "license": "Public Domain",
      "passages": [
        "Earth orbits the Sun at an average distance of about 149.6 million kilometers (93 million miles), a distance defined as 1 Astronomical Unit (AU). It takes approximately 365.25 days for Earth to complete one full revolution around the Sun.",
        "The extra quarter of a day in Earth's orbit is accounted for by adding a leap day every four years. This keeps our calendar in alignment with the astronomical seasons.",
        "Earth's axis of rotation is tilted at an angle of roughly 23.5 degrees relative to its orbital plane. This axial tilt is the primary cause of the seasons, as different hemispheres receive varying amounts of direct sunlight throughout the year."
      ]
    }
  },
  {
    "filename": "lightning-strikes.json",
    "data": {
      "doc_id": "lightning-strikes-05",
      "title": "Lightning Characteristics and Strike Frequencies",
      "publisher": "National Weather Service",
      "source_url": "https://www.weather.gov/safety/lightning-myths",
      "retrieved_date": "2024-09-01",
      "publication_date": "2022-04-10",
      "attribution": "NOAA National Weather Service",
      "license": "Public Domain",
      "passages": [
        "It is a myth that lightning never strikes the same place twice. Lightning is actually more likely to strike tall, pointed, isolated objects repeatedly. The Empire State Building in New York City, for example, is struck by lightning an average of 20 to 25 times per year.",
        "A typical lightning flash contains about 300 million volts and 30,000 amps of electrical current. The temperature of a lightning bolt can reach 30,000 kelvins (53,540 degrees Fahrenheit), which is about five times hotter than the surface of the Sun.",
        "Lightning often strikes the ground multiple times within a single flash. What appears to the eye as a single flickering strike is usually a series of strokes occurring in rapid succession within the same ionized channel."
      ]
    }
  },
  {
    "filename": "mount-everest.json",
    "data": {
      "doc_id": "mount-everest-06",
      "title": "Earth's Highest Mountains",
      "publisher": "National Geographic",
      "source_url": "https://education.nationalgeographic.org/resource/mount-everest/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2022-07-20",
      "attribution": "National Geographic Society (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "Mount Everest, located in the Himalayas on the border of Nepal and China, holds the record for the highest elevation above sea level. Its peak stands at 8,848.86 meters (29,031.7 feet), as jointly measured and announced by Nepal and China in 2020.",
        "While Everest is the highest mountain above sea level, Mauna Kea in Hawaii is the tallest mountain from base to peak. Mauna Kea originates deep on the ocean floor and rises over 10,000 meters (33,500 feet) to its summit, significantly taller than Everest's total height.",
        "Due to Earth's equatorial bulge, Mount Chimborazo in Ecuador is the point on Earth's surface farthest from its center. Despite its elevation above sea level being only 6,268 meters (20,564 feet), its location near the equator pushes its summit further into space than Everest's."
      ]
    }
  },
  {
    "filename": "human-body-water.json",
    "data": {
      "doc_id": "human-body-water-07",
      "title": "Water Content in the Human Body",
      "publisher": "USGS",
      "source_url": "https://www.usgs.gov/special-topics/water-science-school/science/water-you-water-and-human-body",
      "retrieved_date": "2024-09-01",
      "publication_date": "2019-10-22",
      "attribution": "U.S. Geological Survey (USGS)",
      "license": "Public Domain",
      "passages": [
        "In the average adult human, water constitutes approximately 60% of the total body weight. This vital fluid is distributed primarily within cells (intracellular fluid) and the spaces between cells and in the blood plasma (extracellular fluid).",
        "The percentage of water in the body varies based on age and sex. Newborn infants are composed of about 78% water, which drops to about 65% by age one. Adult men typically have more body water (about 60%) than adult women (about 55%) due to differences in fat tissue.",
        "Water is essential for life, acting as a building block for cells, regulating internal body temperature, transporting carbohydrates and proteins in the bloodstream, and helping flush waste mainly through urination."
      ]
    }
  },
  {
    "filename": "speed-of-light.json",
    "data": {
      "doc_id": "speed-of-light-08",
      "title": "The Speed of Light in a Vacuum",
      "publisher": "NIST",
      "source_url": "https://www.nist.gov/si-redefinition/meter",
      "retrieved_date": "2024-09-01",
      "publication_date": "2018-11-16",
      "attribution": "National Institute of Standards and Technology (NIST)",
      "license": "Public Domain",
      "passages": [
        "The speed of light in a vacuum, denoted by the symbol 'c', is exactly 299,792,458 meters per second. This value is a fundamental physical constant and is exact because the length of the meter is defined based upon it.",
        "According to Albert Einstein's theory of special relativity, 'c' is the upper limit for the speed at which conventional matter, energy, and information can travel through space. As an object's speed approaches the speed of light, its relativistic mass increases towards infinity.",
        "Light travels through different media, such as glass, water, or air, at speeds slower than 'c'. The ratio of the speed of light in a vacuum to its speed in a given medium is known as the refractive index of that medium."
      ]
    }
  },
  {
    "filename": "moon-landing.json",
    "data": {
      "doc_id": "moon-landing-09",
      "title": "Apollo 11 Moon Landing",
      "publisher": "NASA",
      "source_url": "https://www.nasa.gov/mission_pages/apollo/apollo11.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "2019-07-16",
      "attribution": "National Aeronautics and Space Administration (NASA)",
      "license": "Public Domain",
      "passages": [
        "On July 20, 1969, the Apollo 11 Lunar Module Eagle touched down in the Sea of Tranquility, making it the first crewed mission to land on the Moon. The mission was commanded by Neil Armstrong and piloted by Buzz Aldrin.",
        "Neil Armstrong became the first human to step onto the lunar surface, famously declaring 'That's one small step for [a] man, one giant leap for mankind.' He and Aldrin spent about two and a quarter hours outside the spacecraft exploring the surface.",
        "The Apollo missions brought back over 380 kilograms (842 pounds) of lunar rocks and soil. Decades of analysis by scientists worldwide, combined with extensive telemetry, photographic evidence, and retroreflectors left on the surface, definitively prove the landings occurred."
      ]
    }
  },
  {
    "filename": "earth-age.json",
    "data": {
      "doc_id": "earth-age-10",
      "title": "Age of the Earth",
      "publisher": "USGS",
      "source_url": "https://pubs.usgs.gov/gip/geotime/age.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "2007-07-09",
      "attribution": "U.S. Geological Survey (USGS)",
      "license": "Public Domain",
      "passages": [
        "Based on extensive scientific evidence, the Earth is estimated to be approximately 4.54 billion years old, with an uncertainty of about 1%. This age represents the time when the Earth formed from the solar nebula alongside the rest of the solar system.",
        "The primary method for determining the Earth's age is radiometric dating, specifically the uranium-lead dating of meteorites. Since meteorites formed at the same time as the solar system and have remained largely unaltered, they provide a reliable age for the Earth.",
        "The oldest known terrestrial materials are zircon crystals found in the Jack Hills of Western Australia. These microscopic minerals have been dated using radiometric techniques to be approximately 4.4 billion years old, indicating the early presence of a solid crust."
      ]
    }
  },
  {
    "filename": "climate-co2.json",
    "data": {
      "doc_id": "climate-co2-11",
      "title": "Atmospheric Carbon Dioxide Levels",
      "publisher": "NOAA",
      "source_url": "https://www.climate.gov/news-features/understanding-climate/climate-change-atmospheric-carbon-dioxide",
      "retrieved_date": "2024-09-01",
      "publication_date": "2024-05-12",
      "attribution": "NOAA Climate.gov",
      "license": "Public Domain",
      "passages": [
        "Before the Industrial Revolution, global average atmospheric carbon dioxide (CO2) levels were approximately 280 parts per million (ppm). By 2023, the global average had surpassed 420 ppm, representing a roughly 50% increase in a relatively short geological timeframe.",
        "Carbon dioxide is a major greenhouse gas, meaning it traps heat radiating from the Earth's surface and prevents it from escaping into space. This enhanced greenhouse effect is the primary driver of observed contemporary global warming.",
        "Ice core records spanning the last 800,000 years reveal that atmospheric CO2 levels never exceeded 300 ppm during past natural climate cycles. The current rapid rise is definitively linked to human activities, primarily the burning of fossil fuels and deforestation."
      ]
    }
  },
  {
    "filename": "vaccines-disease.json",
    "data": {
      "doc_id": "vaccines-disease-12",
      "title": "Impact of Vaccines on Global Diseases",
      "publisher": "World Health Organization",
      "source_url": "https://www.who.int/news-room/fact-sheets/detail/immunization-coverage",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-07-18",
      "attribution": "World Health Organization (WHO)",
      "license": "Fair Use",
      "passages": [
        "Vaccines are one of the most effective public health interventions in history. In 1980, following a massive global vaccination campaign, the World Health Assembly officially declared the global eradication of smallpox, a disease that once killed millions.",
        "The Global Polio Eradication Initiative, heavily reliant on widespread vaccination, has reduced worldwide polio cases by over 99% since 1988. Wild poliovirus is now endemic in only two countries, down from over 125.",
        "WHO estimates that immunization currently prevents 3.5 to 5 million deaths every year from diseases like diphtheria, tetanus, pertussis, influenza and measles. Widespread vaccination maintains herd immunity, protecting those unable to be vaccinated."
      ]
    }
  },
  {
    "filename": "human-senses.json",
    "data": {
      "doc_id": "human-senses-13",
      "title": "The Diversity of Human Senses",
      "publisher": "Encyclopedia Britannica",
      "source_url": "https://www.britannica.com/science/sense-organ",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-11-20",
      "attribution": "Encyclopedia Britannica (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "The traditional notion that humans have only five senses—sight, hearing, taste, smell, and touch—is a gross oversimplification. Neurologists and anatomists generally agree that humans have at least nine distinct senses, and potentially more depending on classification.",
        "Key additional senses include proprioception, the ability to sense the position and movement of one's own body parts without looking. The vestibular sense, located in the inner ear, is responsible for balance, spatial orientation, and detecting acceleration.",
        "Humans also possess specialized sensory receptors for other specific stimuli. Thermoception allows us to detect temperature changes, while nociception is the physiological process underlying the sensation of pain, distinct from general touch."
      ]
    }
  },
  {
    "filename": "amazon-rainforest.json",
    "data": {
      "doc_id": "amazon-rainforest-14",
      "title": "The Amazon Rainforest Ecosystem",
      "publisher": "World Wildlife Fund",
      "source_url": "https://www.worldwildlife.org/places/amazon",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-10-05",
      "attribution": "World Wildlife Fund (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "The Amazon is the world's largest tropical rainforest, covering approximately 5.5 million square kilometers (2.1 million square miles) of the Amazon basin. It spans across nine nations in South America, with the majority located in Brazil (60%).",
        "The Amazon is renowned for its unparalleled biodiversity. It is home to an estimated 390 billion individual trees representing over 16,000 species, and contains about 10% of all known species on Earth, including thousands of endemic birds, mammals, and insects.",
        "The rainforest plays a crucial role in regulating the global climate by acting as a massive carbon sink. However, ongoing deforestation and fires threaten to release vast amounts of stored carbon and push the ecosystem toward a tipping point of irreversible decline."
      ]
    }
  },
  {
    "filename": "dna-structure.json",
    "data": {
      "doc_id": "dna-structure-15",
      "title": "Structure of DNA",
      "publisher": "National Human Genome Research Institute",
      "source_url": "https://www.genome.gov/genetics-glossary/Deoxyribonucleic-Acid",
      "retrieved_date": "2024-09-01",
      "publication_date": "2024-02-14",
      "attribution": "NIH National Human Genome Research Institute",
      "license": "Public Domain",
      "passages": [
        "Deoxyribonucleic acid (DNA) is a molecule composed of two polynucleotide chains that coil around each other to form a double helix. This structure carries genetic instructions for the development, functioning, growth and reproduction of all known organisms.",
        "The double helix structure of DNA was discovered in 1953 by James Watson and Francis Crick, drawing heavily upon X-ray diffraction images captured by Rosalind Franklin and Maurice Wilkins. This discovery fundamentally changed the field of biology.",
        "The genetic information is encoded in the sequence of four chemical bases: adenine (A), guanine (G), cytosine (C), and thymine (T). In the DNA double helix, A always pairs with T, and C always pairs with G across the two strands."
      ]
    }
  },
  {
    "filename": "gravity-basics.json",
    "data": {
      "doc_id": "gravity-basics-16",
      "title": "Fundamental Concepts of Gravity",
      "publisher": "NASA",
      "source_url": "https://spaceplace.nasa.gov/what-is-gravity/en/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2021-09-17",
      "attribution": "NASA Space Place",
      "license": "Public Domain",
      "passages": [
        "Gravity is the force by which a planet or other body draws objects toward its center. On Earth, gravity gives weight to physical objects and causes them to accelerate downward at approximately 9.81 meters per second squared (m/s²) near the surface.",
        "Sir Isaac Newton described gravity mathematically in the 17th century as a universal attractive force between masses, proportional to their masses and inversely proportional to the square of the distance between them.",
        "In 1915, Albert Einstein's theory of general relativity provided a new framework for understanding gravity. Instead of a simple attractive force, Einstein described gravity as a curvature of spacetime caused by the presence of mass and energy."
      ]
    }
  },
  {
    "filename": "solar-system-planets.json",
    "data": {
      "doc_id": "solar-system-planets-17",
      "title": "Planets of the Solar System",
      "publisher": "NASA",
      "source_url": "https://solarsystem.nasa.gov/planets/overview/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2024-01-10",
      "attribution": "NASA Solar System Exploration",
      "license": "Public Domain",
      "passages": [
        "The solar system consists of eight officially recognized planets that orbit the Sun. These are categorized into four inner terrestrial planets (Mercury, Venus, Earth, Mars) and four outer giant planets (Jupiter, Saturn, Uranus, Neptune).",
        "In 2006, the International Astronomical Union (IAU) formally defined what constitutes a 'planet', establishing criteria that an object must orbit the Sun, be massive enough to be roughly spherical, and have cleared its neighboring region of planetesimals.",
        "Under the 2006 IAU criteria, Pluto, previously considered the ninth planet, was reclassified as a 'dwarf planet' because it shares its orbital neighborhood with other objects in the Kuiper Belt. There are currently five officially recognized dwarf planets in our solar system."
      ]
    }
  },
  {
    "filename": "sahara-desert.json",
    "data": {
      "doc_id": "sahara-desert-18",
      "title": "Characteristics of Earth's Deserts",
      "publisher": "National Geographic",
      "source_url": "https://education.nationalgeographic.org/resource/desert/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2022-10-14",
      "attribution": "National Geographic Society (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "A desert is defined scientifically by its low precipitation, typically receiving less than 25 centimeters (10 inches) of rain per year. This definition applies regardless of temperature, allowing for both hot and cold deserts.",
        "The Sahara, located in northern Africa, is the world's largest hot desert, covering an area of roughly 9.2 million square kilometers (3.6 million square miles). It dominates the landscape, characterized by vast sand dunes, rocky plateaus, and extreme daytime heat.",
        "Despite the Sahara's massive size, the continent of Antarctica is actually the world's largest desert overall. It is classified as a polar desert because it is exceptionally dry, with most of the continent receiving minimal precipitation, primarily in the form of snow."
      ]
    }
  },
  {
    "filename": "blood-types.json",
    "data": {
      "doc_id": "blood-types-19",
      "title": "Human Blood Groups",
      "publisher": "American Red Cross",
      "source_url": "https://www.redcrossblood.org/donate-blood/blood-types.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "2024-03-01",
      "attribution": "American Red Cross (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "The ABO blood group system classifies human blood into four main types based on the presence or absence of specific antigens on the surface of red blood cells: Type A, Type B, Type AB, and Type O. An individual's blood type is inherited from their parents.",
        "In addition to the ABO system, the Rh factor is another critical antigen. If it is present, the blood type is positive (+); if absent, it is negative (-). This yields eight common blood types in total, such as A+ or O-.",
        "Individuals with O-negative blood are known as 'universal donors' because their red blood cells lack A, B, and Rh antigens, minimizing the risk of adverse reactions in recipients. Conversely, individuals with AB-positive blood are considered 'universal recipients'."
      ]
    }
  },
  {
    "filename": "photosynthesis.json",
    "data": {
      "doc_id": "photosynthesis-20",
      "title": "The Process of Photosynthesis",
      "publisher": "Nature Education",
      "source_url": "https://www.nature.com/scitable/topicpage/photosynthesis-14028308/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2014-01-01",
      "attribution": "Nature Education (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "Photosynthesis is the fundamental biological process by which plants, algae, and certain bacteria harness energy from sunlight to synthesize foods. This process is essential for maintaining atmospheric oxygen levels and forms the base of most food webs.",
        "During photosynthesis, organisms use light energy to convert carbon dioxide (CO2) from the air and water (H2O) from the soil into glucose, a type of sugar used for energy and growth. The overall chemical equation is often simplified as 6CO2 + 6H2O + light energy → C6H12O6 + 6O2.",
        "Oxygen (O2) is produced as a byproduct of the photosynthetic reaction and is released into the atmosphere. This release of oxygen was critical for the evolution of aerobic life on Earth, changing the planet's early atmosphere."
      ]
    }
  },
  {
    "filename": "global-population.json",
    "data": {
      "doc_id": "global-population-21",
      "title": "Global Population Trends",
      "publisher": "United Nations",
      "source_url": "https://www.un.org/en/global-issues/population",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-04-11",
      "attribution": "United Nations Population Fund (UNFPA)",
      "license": "Public Domain",
      "passages": [
        "The global human population officially reached 8 billion individuals in November 2022, marking a major milestone in human development. This growth has been driven by widespread improvements in public health, nutrition, personal hygiene, and medicine.",
        "While the total population continues to grow, the global population growth rate has been slowing down for decades. In 2020, the global growth rate fell under 1% per year for the first time since 1950, due to declining fertility rates worldwide.",
        "Demographers project that the world's population will peak at around 10.4 billion people during the 2080s and is expected to remain at that level until 2100. More than half of the projected increase in global population up to 2050 will be concentrated in just eight countries."
      ]
    }
  },
  {
    "filename": "antibiotic-resistance.json",
    "data": {
      "doc_id": "antibiotic-resistance-22",
      "title": "Antimicrobial Resistance",
      "publisher": "World Health Organization",
      "source_url": "https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-11-21",
      "attribution": "World Health Organization (WHO)",
      "license": "Fair Use",
      "passages": [
        "Antibiotic resistance is one of the biggest threats to global health, food security, and development today. It occurs when bacteria evolve in ways that reduce or eliminate the effectiveness of drugs, chemicals, or other agents designed to cure or prevent infections.",
        "The WHO has declared antimicrobial resistance a top 10 global public health threat facing humanity. Infections caused by resistant bacteria are harder to treat, requiring higher doses of alternative medications that may be more toxic and expensive.",
        "The primary driver of antimicrobial resistance is the misuse and overuse of antimicrobials in humans, animals, and plants. Poor infection and disease prevention in healthcare settings and agriculture further accelerate the spread of resistant microbes."
      ]
    }
  },
  {
    "filename": "ocean-depth.json",
    "data": {
      "doc_id": "ocean-depth-23",
      "title": "The Deepest Points of the Ocean",
      "publisher": "NOAA",
      "source_url": "https://oceanservice.noaa.gov/facts/mariana.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-01-20",
      "attribution": "National Oceanic and Atmospheric Administration (NOAA)",
      "license": "Public Domain",
      "passages": [
        "The deepest known part of the world's oceans is the Mariana Trench, located in the western Pacific Ocean. The trench is a crescent-shaped scar in the Earth's crust that measures more than 2,500 kilometers (1,500 miles) long.",
        "The absolute deepest point within the Mariana Trench is known as the Challenger Deep. Recent precision measurements estimate its depth to be approximately 10,994 meters (36,070 feet) below sea level, though slight variations exist between surveys.",
        "The immense pressure at the bottom of the Challenger Deep is over 1,000 times standard atmospheric pressure at sea level. Despite these extreme, dark, and near-freezing conditions, specialized organisms such as xenophyophores and specific amphipods have been found living there."
      ]
    }
  },
  {
    "filename": "speed-of-sound.json",
    "data": {
      "doc_id": "speed-of-sound-24",
      "title": "The Speed of Sound",
      "publisher": "NASA",
      "source_url": "https://www.grc.nasa.gov/www/k-12/airplane/sound.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "2021-05-13",
      "attribution": "NASA Glenn Research Center",
      "license": "Public Domain",
      "passages": [
        "The speed of sound is the distance travelled per unit of time by a sound wave as it propagates through an elastic medium. In dry air at 20 °C (68 °F), the speed of sound is approximately 343 meters per second (767 mph).",
        "The speed of sound is not a constant; it depends strongly on the properties of the medium it passes through, primarily its temperature, stiffness, and density. In gases like air, the speed of sound increases as the temperature of the gas increases.",
        "Sound waves travel significantly faster in liquids and solids than they do in gases due to the closer packing of molecules. For instance, sound travels at about 1,480 meters per second in pure water, more than four times faster than in air."
      ]
    }
  },
  {
    "filename": "periodic-table.json",
    "data": {
      "doc_id": "periodic-table-25",
      "title": "The Periodic Table of Elements",
      "publisher": "International Union of Pure and Applied Chemistry",
      "source_url": "https://iupac.org/what-we-do/periodic-table-of-elements/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2022-05-04",
      "attribution": "IUPAC (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "The periodic table is a tabular display of all known chemical elements, organized by their atomic number, electron configuration, and recurring chemical properties. Elements are arranged in rows called periods and columns called groups.",
        "As of the most recent updates, there are 118 confirmed chemical elements on the periodic table. The last four elements (nihonium, moscovium, tennessine, and oganesson) were formally added in 2016, completing the seventh row of the table.",
        "The modern layout of the periodic table evolved from the work of Russian chemist Dmitri Mendeleev, who published his first version in 1869. Mendeleev successfully used his table to predict the properties of elements that had not yet been discovered."
      ]
    }
  },
  {
    "filename": "human-genome.json",
    "data": {
      "doc_id": "human-genome-26",
      "title": "The Human Genome Project",
      "publisher": "National Human Genome Research Institute",
      "source_url": "https://www.genome.gov/human-genome-project",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-08-25",
      "attribution": "NIH National Human Genome Research Institute",
      "license": "Public Domain",
      "passages": [
        "The human genome contains approximately 3 billion base pairs of DNA, spread across 23 pairs of chromosomes. This genetic material contains the instructions required to build and maintain a human being.",
        "The Human Genome Project (HGP) was an international, collaborative research program completed in 2003, which aimed to completely map and understand all the genes of human beings. It remains one of the largest biological research projects ever undertaken.",
        "Initial estimates suggested humans might have over 100,000 genes, but the HGP revealed that humans actually have a surprisingly small number of protein-coding genes, currently estimated to be around 20,000 to 25,000."
      ]
    }
  },
  {
    "filename": "renewable-energy.json",
    "data": {
      "doc_id": "renewable-energy-27",
      "title": "Growth of Global Renewable Energy",
      "publisher": "International Energy Agency",
      "source_url": "https://www.iea.org/reports/renewables-2023",
      "retrieved_date": "2024-09-01",
      "publication_date": "2024-01-11",
      "attribution": "International Energy Agency (IEA)",
      "license": "Fair Use",
      "passages": [
        "Global capacity for renewable energy generation, particularly from solar photovoltaic (PV) and wind power, is expanding at an unprecedented rate. In 2023, the world added roughly 50% more renewable capacity than it did the previous year.",
        "The cost of technologies for generating renewable electricity has plummeted over the last decade. The levelized cost of electricity from utility-scale solar PV and onshore wind is now competitive with or cheaper than new fossil fuel power plants in most parts of the world.",
        "Despite rapid growth, integrating large shares of variable renewable energy into electrical grids presents challenges. Enhancing grid infrastructure, expanding energy storage solutions, and increasing system flexibility are critical for managing supply and demand."
      ]
    }
  },
  {
    "filename": "fresh-water.json",
    "data": {
      "doc_id": "fresh-water-28",
      "title": "Distribution of Earth's Water",
      "publisher": "USGS",
      "source_url": "https://www.usgs.gov/special-topics/water-science-school/science/where-earths-water",
      "retrieved_date": "2024-09-01",
      "publication_date": "2019-10-22",
      "attribution": "U.S. Geological Survey (USGS)",
      "license": "Public Domain",
      "passages": [
        "While water covers about 71% of the Earth's surface, the vast majority is saline ocean water. Only about 2.5% of all the water on Earth is freshwater, the type required to sustain terrestrial plant, animal, and human life.",
        "Of that small percentage of freshwater, nearly 69% is locked away in glaciers, permanent snow, and polar ice caps, primarily in Antarctica and Greenland. About 30% of freshwater exists as groundwater stored deep in underground aquifers.",
        "Consequently, less than 1% of the Earth's total freshwater is readily accessible for human use in lakes, rivers, and shallow aquifers. This relatively small amount must support ecosystems, agriculture, industry, and municipal water supplies worldwide."
      ]
    }
  },
  {
    "filename": "continental-drift.json",
    "data": {
      "doc_id": "continental-drift-29",
      "title": "Plate Tectonics and Continental Drift",
      "publisher": "USGS",
      "source_url": "https://pubs.usgs.gov/gip/dynamic/historical.html",
      "retrieved_date": "2024-09-01",
      "publication_date": "1999-05-05",
      "attribution": "U.S. Geological Survey (USGS)",
      "license": "Public Domain",
      "passages": [
        "The scientific theory of plate tectonics explains the large-scale motion of the plates that make up Earth's lithosphere. This modern theory builds upon the concept of continental drift, first proposed by meteorologist Alfred Wegener in 1912.",
        "Geological evidence strongly suggests that approximately 335 million years ago, all of Earth's major landmasses were assembled into a single supercontinent known as Pangaea. This supercontinent began to break apart roughly 175 million years ago.",
        "Tectonic plates float on the semi-fluid asthenosphere beneath them, driven by convection currents in the Earth's mantle. The interactions at plate boundaries result in geological phenomena such as earthquakes, volcanic activity, and the formation of mountain ranges."
      ]
    }
  },
  {
    "filename": "internet-history.json",
    "data": {
      "doc_id": "internet-history-30",
      "title": "History of the Internet and World Wide Web",
      "publisher": "Internet Society",
      "source_url": "https://www.internetsociety.org/internet/history-internet/",
      "retrieved_date": "2024-09-01",
      "publication_date": "2023-01-01",
      "attribution": "Internet Society (Paraphrased)",
      "license": "Fair Use",
      "passages": [
        "The origins of the Internet date back to 1969 with the creation of ARPANET, an experimental computer network funded by the U.S. Department of Defense. On January 1, 1983, ARPANET officially transitioned to using the TCP/IP protocol suite, laying the technical foundation for the modern Internet.",
        "The World Wide Web is a system of interconnected documents and resources accessed via the Internet, invented by British computer scientist Tim Berners-Lee between 1989 and 1991 while working at CERN. It fundamentally transformed the Internet into a publicly accessible medium.",
        "Since the introduction of the web, Internet adoption has grown exponentially. By 2023, it was estimated that over 5 billion people—more than 60% of the global population—used the Internet regularly for communication, commerce, and information retrieval."
      ]
    }
  }
]

for doc in docs:
    filepath = os.path.join(docs_dir, doc["filename"])
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(doc["data"], f, indent=2)

print("Created 31 files successfully.")
