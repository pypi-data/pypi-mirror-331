# FILE: taxonize_gb/test_main.py

from taxonize_gb.main import (
    check_input, check_db, list_files_with_extension, check_taxdb,
    read_nodes_dmp, read_names_dmp, build_taxonomic_graph, get_all_subtaxids,
    parse_taxids, read_taxids_from_file, main
)

class TestMain(unittest.TestCase):

    @patch('taxonize_gb.main.download_db')
    def test_check_input(self, mock_download_db):
        mock_download_db.return_value = '/path/to/downloaded/db'
        self.assertEqual(check_input(False, 'db_name', '/output'), '/path/to/downloaded/db')
        self.assertEqual(check_input('/path/to/db', 'db_name', '/output'), '/path/to/db')

    def test_check_db(self):
        self.assertEqual(check_db('nt'), 'nt')
        self.assertEqual(check_db('nucleotide'), 'nt')
        self.assertEqual(check_db('nr'), 'nr')
        self.assertEqual(check_db('protein'), 'nr')
        with self.assertRaises(SystemExit):
            check_db('invalid_db')

    @patch('os.listdir')
    def test_list_files_with_extension(self, mock_listdir):
        mock_listdir.return_value = ['file1.dmp', 'file2.txt', 'file3.dmp']
        expected = {
            'file1': '/abs/path/to/file1.dmp',
            'file3': '/abs/path/to/file3.dmp'
        }
        with patch('os.path.abspath', side_effect=lambda x: f'/abs/path/to/{os.path.basename(x)}'):
            self.assertEqual(list_files_with_extension('/directory', 'dmp'), expected)

    @patch('tarfile.open')
    @patch('taxonize_gb.main.list_files_with_extension')
    def test_check_taxdb(self, mock_list_files_with_extension, mock_tarfile_open):
        mock_tarfile = MagicMock()
        mock_tarfile_open.return_value.__enter__.return_value = mock_tarfile
        mock_list_files_with_extension.return_value = {'nodes': '/path/to/nodes.dmp'}
        self.assertEqual(check_taxdb('/path/to/taxdb.tar.gz', '/output'), {'nodes': '/path/to/nodes.dmp'})
        mock_tarfile.extractall.assert_called_with(path='/output')

    @patch('builtins.open', new_callable=mock_open, read_data="1 | 1 | rank |\n2 | 1 | rank |")
    @patch('tqdm.tqdm', side_effect=lambda x, **kwargs: x)
    def test_read_nodes_dmp(self, mock_tqdm, mock_open):
        expected_taxid_to_parent = {'1': '1', '2': '1'}
        expected_rank_map = {'1': 'rank', '2': 'rank'}
        self.assertEqual(read_nodes_dmp('/path/to/nodes.dmp'), (expected_taxid_to_parent, expected_rank_map))

    @patch('builtins.open', new_callable=mock_open, read_data="1 | name | | scientific name |\n2 | name2 | | scientific name |")
    @patch('tqdm.tqdm', side_effect=lambda x, **kwargs: x)
    def test_read_names_dmp(self, mock_tqdm, mock_open):
        expected_taxid_to_name = {'1': 'name', '2': 'name2'}
        self.assertEqual(read_names_dmp('/path/to/names.dmp'), expected_taxid_to_name)

    def test_build_taxonomic_graph(self):
        taxid_to_parent = {'1': '0', '2': '1'}
        graph = build_taxonomic_graph(taxid_to_parent)
        self.assertTrue(graph.has_edge('0', '1'))
        self.assertTrue(graph.has_edge('1', '2'))

    def test_get_all_subtaxids(self):
        taxid_to_parent = {'1': '0', '2': '1'}
        graph = build_taxonomic_graph(taxid_to_parent)
        self.assertEqual(get_all_subtaxids(graph, '1'), {'1', '2'})

    def test_parse_taxids(self):
        self.assertEqual(parse_taxids('1,2,3'), ['1', '2', '3'])

    @patch('builtins.open', new_callable=mock_open, read_data="1\n2\n3\n")
    def test_read_taxids_from_file(self, mock_open):
        self.assertEqual(read_taxids_from_file('/path/to/taxids.txt'), ['1', '2', '3'])

    @patch('argparse.ArgumentParser.parse_args')
    @patch('taxonize_gb.main.check_out_directory')
    @patch('taxonize_gb.main.check_input')
    @patch('taxonize_gb.main.check_taxdb')
    @patch('taxonize_gb.main.read_nodes_dmp')
    @patch('taxonize_gb.main.read_names_dmp')
    @patch('taxonize_gb.main.build_taxonomic_graph')
    