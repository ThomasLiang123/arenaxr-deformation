#include "morpher.hpp"

int main (int argc, char **argv) {
    if (argc != 2) {
        std::cout<<"invalid arguments"<<std::endl;
        return 1;
    }

    decode(argv[1]);

    return 0;
}

Primitive getprimitive(Json::Value json) {
    // only handle the first primitive (one object)
    Json::Value primjson = json["meshes"][0]["primitives"][0];
    PrimitiveAttributes primattr;
    primattr.position = primjson["attributes"]["POSITION"].asUInt();
    primattr.normal = primjson["attributes"]["NORMAL"].asUInt();
    
    Primitive prim;
    prim.attributes = primattr;
    prim.indices = primjson["indices"].asUInt();

    return prim;
}

int decode(char *filename) {
    int fd = open(filename, 0, 0);
    if (fd == -1) {
        std::cout<<"invalid file"<<std::endl;
        return 1;
    }

    // read header
    uint32_t *header = (uint32_t *) malloc(12);
    read(fd, header, 12);

    // check if gltf file
    if (memcmp(header, "glTF", 4) != 0) {
        std::cout<<"not gltf file"<<std::endl;
        return 1;
    }

    // get length of file and version numbers from header
    uint32_t length = header[2];
    uint32_t version = header[1];

    free(header);

    // read json header
    uint32_t *jsonheader = (uint32_t *) malloc(8);
    read(fd, jsonheader, 8);

    // get json length
    uint32_t jsonLength = *jsonheader;
    free(jsonheader);

    // decode json and get first primitive
    Json::Value json = decodejson(fd, jsonLength);
    Primitive prim = getprimitive(json);

    // get binary data header
    header = (uint32_t *) malloc(8);
    read(fd, header, 8);

    // get binary data length and read binary
    uint32_t binlen = header[0];
    char *binary = (char *) malloc(binlen);
    read(fd, binary, binlen);
    
    close(fd);

    // create new morph data
    char *newbin = NULL;
    Json::Value newjson = handleprimitive(prim, json, binary, binlen, &newbin);
    uint32_t newbinlen = newjson["buffers"][0]["byteLength"].asUInt();
    
    // write new glTF to glb file
    Json::StreamWriterBuilder builder;
    builder["indentation"] = "";
    builder.settings_["precision"] = 15;
    std::string newjsonstr = Json::writeString(builder, newjson);
    uint32_t newjsonlen = newjsonstr.length();
    while (newjsonlen % 4 != 0) {
        newjsonstr+=' ';
        newjsonlen++;
    }

    char *newfilename = "morph.glb";
    int newfd = open(newfilename, O_CREAT | O_TRUNC | O_RDWR, 0666);

    uint32_t *newheader = (uint32_t *) malloc(12);
    memcpy(newheader, "glTF", 4);
    newheader[1] = version;
    newheader[2] = newjsonlen + newbinlen + 12 + 8 + 8;
    write(newfd, (void *) newheader, 12);

    uint32_t *newjsonheader = (uint32_t *) malloc(8);
    newjsonheader[0] = newjsonlen;
    memcpy(newjsonheader+1, "JSON", 4);
    write(newfd, (void *) newjsonheader, 8);

    write(newfd, (void *) newjsonstr.c_str(), newjsonlen);

    uint32_t *newbinheader = (uint32_t *) malloc(8);
    newbinheader[0] = newbinlen;
    memcpy(newbinheader+1, "BIN\0", 4);
    write(newfd, (void *) newbinheader, 8);

    write(newfd, (void *) newbin, newbinlen);

    close(newfd);

    free(binary);
    free(newbin);
    free(newheader);
    free(newjsonheader);
    free(newbinheader);

    return 0;
}

Json::Value decodejson(int fd, uint32_t len) {
    // read json text
    char *buffer = (char *) malloc(len+1);
    read(fd, buffer, len);
    buffer[len] = '\0';

    // parse json with jsoncpp
    Json::Value root;
    Json::Reader reader;
    bool success = reader.parse(buffer, root);
    if (!success) {
        std::cout<<"fail to decode"<<std::endl;
    }

    free(buffer);

    return root;
}

Json::Value handleprimitive(Primitive prim, Json::Value json, char *buf, int buflen, char **newbuf) {
    int numaccessors = json["accessors"].size();
    int numbufferviews = json["bufferViews"].size();

    // get accessors for primitive's indices, vertex positions, and vertex normals
    Accessor idxacc = getaccessor(prim.indices, json);
    Accessor vertexposacc = getaccessor(prim.attributes.position, json);
    Accessor vertexnormacc = getaccessor(prim.attributes.normal, json);
    vector<uint16_t> indices = readindexlist(buf, idxacc.offset, vertexposacc.count);

    vector<VecFloat3> vertices;
    vector<MorphTarget> targets;

    // create empty morph target vector
    for (std::size_t i = 0; i < indices.size(); i++) {
        targets.push_back(MorphTarget());
    }

    // number of targets * number of vertices: each target's data will have data for all vertices
    char *newbin = (char *) malloc(indices.size() * indices.size() * sizeof(VecFloat3));
    int offset = 0;

    vector<BufferView> bufferviews;
    vector<Accessor> accessors;
    vector<MorphTarget> morphtargets;
    vector<string> targetnames;
    
    // for each vertex, create morph targets
    for (std::size_t i = 0; i < indices.size(); i++) {
        // get vertex's position and normal
        VecFloat3 vertex = readvecfloat3(buf, vertexposacc.offset + i * sizeof(VecFloat3));
        VecFloat3 normal = readvecfloat3(buf, vertexnormacc.offset + i * sizeof(VecFloat3));

        // create name
        // get rounded position data to the nearest tenth (times ten)
        int roundy = round(vertex.y * 10);
        int roundz = round(vertex.z * 10);

        // morph name format: "m" + y location * 10 + ":" + z location * 10
        string name = "m";
        name += std::to_string(roundy);
        name += ":";
        name += std::to_string(roundz);
        targetnames.push_back(name);

        // create actual morph data
        VecFloat3 morph;
        // morph.x = -normal.x;
        // morph.y = -normal.y;
        // morph.z = -normal.z;
        morph.x = -1;
        morph.y = 0;
        morph.z = 0;
        vertices.push_back(vertex);

        // add morph data to morph binary data
        makemorphdata(vertex, morph, i, indices.size(), newbin, offset);

        // make bufferview for morph data
        BufferView newbf;
        newbf.buffer = 0;
        newbf.byteLength = indices.size() * sizeof(VecFloat3);
        newbf.byteOffset = offset + buflen;
        newbf.target = 34962;

        // make accessor for bufferview
        Accessor newacc;
        newacc.bufferview = i + numbufferviews;
        newacc.count = indices.size();
        newacc.type = "VEC3";
        newacc.componenttype = 5126;
        if (morph.x > 0) {
            newacc.max.x = morph.x;
            newacc.min.x = 0;
        } else {
            newacc.min.x = morph.x;
            newacc.max.x = 0;
        }
        if (morph.y > 0) {
            newacc.max.y = morph.y;
            newacc.min.y = 0;
        } else {
            newacc.min.y = morph.y;
            newacc.max.y = 0;
        }
        if (morph.z > 0) {
            newacc.max.z = morph.z;
            newacc.min.z = 0;
        } else {
            newacc.min.z = morph.z;
            newacc.max.z = 0;
        }

        // make morph target for accessor
        MorphTarget newmt;
        newmt.position = i + numaccessors;
        newmt.normal = prim.attributes.normal;

        bufferviews.push_back(newbf);
        accessors.push_back(newacc);
        morphtargets.push_back(newmt);

        offset += indices.size() * sizeof(VecFloat3);
    }

    // for each vertex, add morph, accessor, and bufferview into json
    for (std::size_t i = 0; i < indices.size(); i++) {
        std::string mn = "m";
        mn += std::to_string(i);
        json["meshes"][0]["extras"]["targetNames"][(int)i] = targetnames[i];
        json["meshes"][0]["primitives"][0]["targets"][(int)i] = morphtargettojson(morphtargets[i]);
        json["accessors"][numaccessors + (int)i] = accessortojson(accessors[i]);
        json["bufferViews"][numbufferviews + (int)i] = bufferviewtojson(bufferviews[i]);
    }
    
    // change bytelength entry in json to account for new morph data
    json["buffers"][0]["byteLength"] = offset + buflen;

    // create new binary buffer for morph data
    *newbuf = (char *) malloc(offset + buflen);
    memcpy(*newbuf, buf, buflen);
    memcpy((*newbuf) + buflen, newbin, offset);

    return json;
}

void makemorphdata(VecFloat3 vertex, VecFloat3 normal, uint32_t index, uint32_t count, char *data, int offset) {
    VecFloat3 *edit = (VecFloat3 *) (data + offset);

    // each morph consists of all vertices - set to 0, except for the target vertex to morph
    for (std::size_t i = 0; i < count; i++) {
        edit[i].x = 0;
        edit[i].y = 0;
        edit[i].z = 0;
        if (i == index) {
            edit[i].x = normal.x;
            edit[i].y = normal.y;
            edit[i].z = normal.z;
        }
    }
}

Accessor getaccessor(uint32_t accessor, Json::Value json) {
    Accessor acc;
    acc.bufferview = json["accessors"][accessor]["bufferView"].asUInt();
    acc.count = json["accessors"][accessor]["count"].asUInt();
    acc.offset = json["bufferViews"][acc.bufferview]["byteOffset"].asUInt();
    return acc;
}

VecFloat3 readvecfloat3(char *buf, uint32_t off) {
    VecFloat3 vec;
    float *fltptr = (float *) (buf + off);
    vec.x = fltptr[0];
    vec.y = fltptr[1];
    vec.z = fltptr[2];

    return vec;
}

Json::Value bufferviewtojson(BufferView bf) {
    Json::Value json;
    json["buffer"] = bf.buffer;
    json["byteLength"] = bf.byteLength;
    json["byteOffset"] = bf.byteOffset;
    json["target"] = bf.target;

    return json;
}

Json::Value accessortojson(Accessor acc) {
    Json::Value json;
    json["bufferView"] = acc.bufferview;
    json["componentType"] = acc.componenttype;
    json["count"] = acc.count;
    json["max"][0] = acc.max.x;
    json["max"][1] = acc.max.y;
    json["max"][2] = acc.max.z;
    json["min"][0] = acc.min.x;
    json["min"][1] = acc.min.y;
    json["min"][2] = acc.min.z;
    json["type"] = acc.type;

    return json;
}

Json::Value morphtargettojson(MorphTarget mt) {
    Json::Value json;
    json["POSITION"] = mt.position;
    json["NORMAL"] = mt.normal;

    return json;
}

vector<uint16_t> readindexlist(char *buf, uint32_t off, uint32_t length) {
    vector<uint16_t> vec;

    uint16_t *intptr = (uint16_t *) (buf + off);
    for (uint32_t i = 0; i < length; i++) {
        vec.push_back(intptr[i]);
    }

    return vec;
}