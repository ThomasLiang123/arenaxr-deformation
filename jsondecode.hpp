#ifndef JSONDECODE_HPP
#define JSONDECODE_HPP

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
#include <math.h>
#include <json/json.h>
#include <json/reader.h>
#include <json/writer.h>
#include <json/value.h>

using std::vector;
using std::string;

struct VecFloat3 {
    float x;
    float y;
    float z;
};

struct PrimitiveAttributes {
    uint32_t position; // accessor that points to bufferview that points to list of vertices (vecfloat3)
    uint32_t normal; // ... points to list of normals for vertices
};

struct Primitive {
    PrimitiveAttributes attributes;
    uint32_t indices; // order of the vertices in the data
};

struct Mesh {
    vector<Primitive> primitives;
    vector<string> target_names; // names of morph targets
    string name; // name of mesh
};

struct MorphTarget {
    uint32_t position; // ... points to vertex changes for a specific morph
    uint32_t normal; // .. points to list of normals for a specific morph
};

struct Accessor {
    uint32_t bufferview;
    uint32_t count; // number of elements
    uint32_t offset; // byte offset of data
    uint32_t componenttype;
    string type;

    // for morph targets
    VecFloat3 min;
    VecFloat3 max;
};

struct BufferView {
    uint32_t buffer;
    uint32_t byteLength;
    uint32_t byteOffset;
    uint32_t target;
};

int decode(char *filename);

Json::Value decodejson(int fd, uint32_t len);

Json::Value handleprimitive(Primitive prim, Json::Value json, char *buf, int buflen, char **newbuf);

Mesh getmesh(Json::Value json);
Primitive getprimitive(Json::Value json);

void makemorphdata(VecFloat3 vertex, VecFloat3 normal, uint32_t index, uint32_t count, char *data, int offset);

Accessor getaccessor(uint32_t accessor, Json::Value json);
VecFloat3 readvecfloat3(char *buf, uint32_t off);

Json::Value bufferviewtojson(BufferView bf);
Json::Value accessortojson(Accessor acc);
Json::Value morphtargettojson(MorphTarget mt);

vector<uint16_t> readindexlist(char *buf, uint32_t off, uint32_t length);

#endif