#ifndef TREE_H
#define TREE_H

#include <map>  // Changed from <unordered_map>
#include <string>
#include <utility>

#include "tree_record.h"

class Tree {
public:
    const std::map<std::string, TreeRecord> records;  // Changed from std::unordered_map

    explicit Tree(const std::map<std::string, TreeRecord>& records): records(records) {}

    std::map<std::string, TreeRecord>::const_iterator record(const std::string& key) const {  // Changed return type
        return records.find(key);
    }
};

#endif