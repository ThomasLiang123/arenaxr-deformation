#include <iostream>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <vector>
#include <string>
#include <cstdlib>
#include <fstream>
#include <memory>

using std::vector;
using std::string;

struct Scene {
    vector<uint32_t> node_ids;
};

struct Node {
    uint32_t mesh_id;
};

struct PrimitiveAttributes {
    uint32_t position;
};

struct Primitive {
    PrimitiveAttributes attributes;
    uint32_t indices;
};

struct Mesh {
    vector<Primitive> primitives;
};

struct BufferView {
    uint32_t buffer;
    uint32_t byteOffset;
    uint32_t byteLength;
    uint32_t target;
};

struct Accessor {
    int bufferView;
    int byteOffset;
    int componentType;
    int count;
    string type;
    vector<int> max;
    vector<int> min;
};

static Scene scene;
static vector<Node> nodes;
static vector<Mesh> meshes;
static vector<BufferView> bufferViews;
static vector<Accessor> accessors;

void read_quote(char *buffer, char *quote) {
    if (buffer[0] != '\"') {
        std::cout<<"invalid quote read"<<std::endl;
        return;
    }

    int quoteidx = 0;
    while (buffer[quoteidx + 1] != '\"') {
        quote[quoteidx] = buffer[quoteidx + 1];
        quoteidx++;
    }

    quote[quoteidx] = '\0';
}

int ismesh(char *key) {
    if (strcmp(key, "meshes") == 0) {
        return 0;
    }

    return -1;
}

void read_meshes(char *buffer) {
    char *value = (char *) malloc(256);
    int idx = 0;
    if (buffer[0] == '[') {
        int openbracks = 1;
        buffer++;
        while (openbracks > 0) {
            if (buffer[0] == '[') {
                openbracks++;
            } else if (buffer[0] == ']') {
                openbracks--;
            }
            buffer++;
            value[idx] = buffer[0];
            idx++;
        }
        buffer++;
    } else {
        std::cout<<"mesh read error"<<std::endl;
    }

    value[idx] = '\0';
    printf("%s\n", value);
    free(value);
}

char * skip_value(char *buffer) {
    if (buffer[0] == '{') {
        int openbracks = 1;
        buffer++;
        while (openbracks > 0) {
            if (buffer[0] == '{') {
                openbracks++;
            } else if (buffer[0] == '}') {
                openbracks--;
            }
            buffer++;
        }
    } else if (buffer[0] == '[') {
        int openbracks = 1;
        buffer++;
        while (openbracks > 0) {
            if (buffer[0] == '[') {
                openbracks++;
            } else if (buffer[0] == ']') {
                openbracks--;
            }
            buffer++;
        }
    } else {
        while (buffer[0] != ',' && buffer[0] != '}') {
            buffer++;
        }
    }
    buffer++;

    return buffer;
}

void read_json_string(char *buffer, uint32_t len) { 
    uint32_t i = 1;
    char *remaining = buffer+1;
    char *key = (char *) malloc(64);
    char *garbage = (char *) malloc(len);
    while (i < len) {
        read_quote(remaining, key);

        remaining += 3 + strlen(key);
        i = remaining - buffer;
        printf("%s\n", key);

        int type = ismesh(key);
        if (type == -1) {
            remaining = skip_value(remaining);
        } else {
            read_meshes(remaining);
            break;
        }
    }
}

int decodejson(int fd, uint32_t len) {
    char *buffer = (char *) malloc(len);
    read(fd, buffer, len);

    read_json_string(buffer, len);

    free(buffer);

    return 0;
}

int decode(char *filename) {
    int fd = open(filename, 0, 0);
    if (fd == -1) {
        std::cout<<"invalid file"<<std::endl;
        return 1;
    }

    uint32_t *header = (uint32_t *) malloc(12);
    read(fd, header, 12);

    if (memcmp(header, "glTF", 4) != 0) {
        std::cout<<"not gltf file"<<std::endl;
        return 1;
    }

    uint32_t length = header[2];
    printf("%u %u %u\n", header[0], header[1], header[2]);

    free(header);

    uint32_t *jsonheader = (uint32_t *) malloc(8);
    read(fd, jsonheader, 8);

    uint32_t jsonLength = *jsonheader;
    free(jsonheader);

    decodejson(fd, jsonLength);

    return 0;
}

int main (int argc, char **argv) {
    if (argc != 2) {
        std::cout<<"invalid arguments"<<std::endl;
        return 1;
    }

    decode(argv[1]);

    return 0;
}