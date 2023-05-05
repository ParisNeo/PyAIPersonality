#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <chrono>
#include <ctime>
#include <yaml-cpp/yaml.h>
#include <stdexcept>
#include <fstream>
#include "stb_image.h"

using namespace std;
namespace fs = std::filesystem;

class AIPersonality {

    private:

        unordered_map<string, string> Conditionning_commands{
            {"date_time", []() {
                auto now = chrono::system_clock::now();
                time_t now_time = chrono::system_clock::to_time_t(now);
                string time_str = ctime(&now_time);
                time_str.pop_back();
                return time_str;
            }},
            {"date", []() {
                auto now = chrono::system_clock::now();
                time_t now_time = chrono::system_clock::to_time_t(now);
                string date_str = ctime(&now_time);
                date_str = date_str.substr(0, date_str.find_last_of(" "));
                return date_str;
            }},
            {"time", []() {
                auto now = chrono::system_clock::now();
                time_t now_time = chrono::system_clock::to_time_t(now);
                string time_str = ctime(&now_time);
                time_str = time_str.substr(time_str.find_last_of(" ") + 1);
                time_str.pop_back();
                return time_str;
            }}
        };

    public:

        string version = "";
        string name = "gpt4all";
        string user_name = "user";
        string language = "en_XX";
        string category = "General";
        string personality_description = "This personality is a helpful and Kind AI ready to help you solve your problems";
        string personality_conditioning = "GPT4All is a smart and helpful Assistant built by Nomic-AI. It can discuss with humans and assist them.\nDate: {{date}}";
        string welcome_message = "Welcome! I am GPT4All A free and open assistant. What can I do for you today?";
        string user_message_prefix = "### Human:";
        string link_text = "\n";
        string ai_message_prefix = "### Assistant:";
        vector<string> anti_prompts = {"#", "###", "Human:", "Assistant:"};
        vector<string> dependencies = {};
        string disclaimer = "";
        float model_temperature = 0.8;
        int model_n_predicts = 1024;
        int model_top_k = 50;
        float model_top_p = 0.95;
        float model_repeat_penalty = 1.3;
        int model_repeat_last_n = 40;
        optional<Image> _logo = {};

        AIPersonality(string personality_package_path = "") {
            version = "0.0.1";

            if (!personality_package_path.empty()) {
                fs::path p(personality_package_path);

                // Validate that the path exists
                if (!fs::exists(p)) {
                    throw invalid_argument("The provided path does not exist.");
                }

                // Validate that the path format is OK with at least a config.yaml file present in the folder
                if (!fs::is_directory(p)) {
                    throw invalid_argument("The provided path is not a folder.");
                }

                // Verify that there is at least a configuration file
                fs::path config_file = p / "config.yaml";
                if (!fs::is_regular_file(config_file)) {
                    throw invalid_argument("The provided folder does not contain a config.yaml file.");
                }

                // Open and store the personality
                load_personality(config_file);
            }
        }

        /**
         * Load the personality data from a YAML file and set it as attributes of the class.
         *
         * @param file_path The path to the YAML file containing the personality data.
         * @return A dictionary containing the personality data.
         */
        std::map<std::string, YAML::Node> load_personality(const std::string& file_path) {
            std::ifstream fin(file_path);
            YAML::Node config = YAML::Load(fin);

            // Set the personality attributes
            version = config["version"].as<std::string>(version);
            name = config["name"].as<std::string>(name);
            user_name = config["user_name"].as<std::string>(user_name);
            language = config["language"].as<std::string>(language);
            category = config["category"].as<std::string>(category);
            personality_description = config["personality_description"].as<std::string>(personality_description);
            personality_conditioning = config["personality_conditioning"].as<std::string>(personality_conditioning);
            welcome_message = config["welcome_message"].as<std::string>(welcome_message);
            user_message_prefix = config["user_message_prefix"].as<std::string>(user_message_prefix);
            link_text = config["link_text"].as<std::string>(link_text);
            ai_message_prefix = config["ai_message_prefix"].as<std::string>(ai_message_prefix);
            anti_prompts = config["anti_prompts"].as<std::vector<std::string>>(anti_prompts);
            dependencies = config["dependencies"].as<std::vector<std::string>>(dependencies);
            disclaimer = config["disclaimer"].as<std::string>(disclaimer);
            model_temperature = config["model_temperature"].as<float>(model_temperature);
            model_n_predicts = config["model_n_predicts"].as<int>(model_n_predicts);
            model_top_k = config["model_top_k"].as<int>(model_top_k);
            model_top_p = config["model_top_p"].as<float>(model_top_p);
            model_repeat_penalty = config["model_repeat_penalty"].as<float>(model_repeat_penalty);
            model_repeat_last_n = config["model_repeat_last_n"].as<int>(model_repeat_last_n);
            
            // Load the logo file using stb_image
            std::string logo_path = "assets/logo.png";
            int logo_width, logo_height, logo_channels;
            unsigned char *logo_data = stbi_load(logo_path.c_str(), &logo_width, &logo_height, &logo_channels, 0);
            if (logo_data != nullptr) {
                _logo = Image(logo_width, logo_height, logo_channels, logo_data);
                stbi_image_free(logo_data);
            }
            
            std::map<std::string, YAML::Node> result;
            for (const auto& [key, value] : config) {
                result.emplace(key.as<std::string>(), value);
            }
            return result;
        }

}