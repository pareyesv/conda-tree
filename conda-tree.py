#!/usr/bin/env python
import sys
import argparse
import conda.install
import conda.resolve
import conda.api
import networkx

def get_local_cache(prefix):
    return conda.install.linked_data(prefix=prefix)

def get_package_key(cache, package_name):
    ks = list(filter(lambda i: l[i]['name'] == package_name, l))
    return ks[0]

def make_cache_graph(cache):
	g = networkx.DiGraph()
	for k in cache.keys():
		n = cache[k]['name']
		g.add_node(n)
		for j in cache[k]['depends']:
			n2 = j.split(' ')[0]
			g.add_edge(n, n2)
	return(g)

def print_graph_dot(g):
    print("digraph {")
    for k,v in g.edges():
       print("  \"{}\" -> \"{}\"".format(k,v))
    print("}")

def remove_from_graph(g, node, _cache=None):
    if _cache is None: _cache = {}
    if node not in _cache:
        _cache[node] = True
        for k,v in g.out_edges(node):
            g = remove_from_graph(g, v, _cache)
    if node in g: g.remove_node(node)
    return(g)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--prefix', default=sys.prefix)
    subparser = parser.add_subparsers(dest='subcmd')
    subparser.add_parser('leafs', help='shows leaf packages')
    subparser.add_parser('cycles', help='shows dependency cycles')
    p = subparser.add_parser('whoneeds', help='shows packages that depends on this package')
    p.add_argument('package', help='the target package')
    p = subparser.add_parser('depends', help='shows this package dependencies')
    p.add_argument('package', help='the target package')
    args = parser.parse_args()

    l = get_local_cache(args.prefix)
    g = make_cache_graph(l)

    if args.subcmd == 'cycles':
        for i in networkx.simple_cycles(g):
            print(" -> ".join(i)+" -> "+i[0])

    elif args.subcmd == 'depends':
        e = list(map(lambda i: i[1], g.out_edges(args.package)))
        print(e)

    elif args.subcmd == 'whoneeds':
        e = list(map(lambda i: i[0], g.in_edges(args.package)))
        print(e)

    elif args.subcmd == 'leafs':
        e = list(map(lambda i:i[0],(filter(lambda i:i[1]==0,g.in_degree()))))
        print(e)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

