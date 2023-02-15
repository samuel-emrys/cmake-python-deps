#include <iostream>
#include <fstream>
#include <string>

enum args {
    prog_name = 0,
    num_lines = 1,
    file = 2
};

int main(int argc, char** argv){

    if (argc < 3) {
        std::cerr << "ERROR: Incorrect invocation. Usage:\n";
        std::cerr << "dumpfile [NUM_LINES] [PATH_TO_FILE]\n";
        return EXIT_FAILURE;
    }
    // Collect input args
    int num_lines = std::stoi(argv[args::num_lines]);
    std::ifstream file(argv[args::file]);

    if (!file.is_open()) {
        std::cerr << "ERROR: Could not find file '" << argv[args::file] << "'.\n";
        return EXIT_FAILURE;
    }

    std::string heading = "Dumping first " + std::string(argv[args::num_lines]) + " lines of '" + std::string(argv[args::file]);
    std::cout << heading << "'\n";
    std::cout << std::string(heading.length(), '=') << "\n";

    std::string line;
    for (int line_num = 0; line_num < num_lines; line_num++) {
        std::getline(file, line);
        std::cout << line << "\n";
    }
    std::cout << std::string(heading.length(), '=') << "\n";
    return EXIT_SUCCESS;
}
